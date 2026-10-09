from django.shortcuts import render
from .models import ChatConversation,ChatMessage
from rest_framework.views import APIView
from rest_framework.response import Response 
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from myapp.models import AIRoomDesign,registermodel,DesignVersion
from myapp.ai_service import generate_room_design
from myapp.views import ai_room_result
from .models import *
from .serializers import *
from .services import (
    extract_design_context,
    generate_ai_response,
    detect_chat_intent,
    generate_general_response,
    search_website_data,
    generate_database_response,)
import base64
from django.core.files.base import ContentFile
from django.urls import reverse
from django.db.models import Max

class ChatConversationListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        conversation = ChatConversation.objects.filter(user = request.user).order_by("-updated_at")
        serializer = ChatConversationSerializer(conversation,many=True)
        return Response(serializer.data)
    def post(self,request):
        title = request.data.get("title","New Design Chat")
        conversation = ChatConversation.objects.create(user=request.user,title = title)
        serializer = ChatConversationSerializer(conversation)
        return Response(serializer.data,status=status.HTTP_201_CREATED)

class SendMessageView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, conversation_id):

        print("DJANGO USER ID:", request.user.id)
        print("DJANGO USERNAME:", request.user.username)
        print("CONVERSATION ID:", conversation_id)

        # =====================================================
        # CHECK LOGIN
        # =====================================================

        if "log_id" not in request.session:
            return Response(
                {"error": "Please login first."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # =====================================================
        # VALIDATE MESSAGE
        # =====================================================

        serializer = SendMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        message = serializer.validated_data["message"]

        # =====================================================
        # GET CONVERSATION
        # =====================================================

        try:

            conversation = ChatConversation.objects.get(
                id=conversation_id,
                user=request.user
            )

        except ChatConversation.DoesNotExist:

            return Response(
                {
                    "error": "Conversation does not exist."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        # =====================================================
        # SAVE USER MESSAGE
        # =====================================================

        user_message = ChatMessage.objects.create(
            conversation=conversation,
            role="user",
            content=message
        )

        # =====================================================
        # GET EXISTING DESIGN CONTEXT
        # =====================================================

        design_context, created = DesignContext.objects.get_or_create(
            conversation=conversation
        )

        context_data = {
            "room_type": design_context.room_type,
            "room_size": design_context.room_size,
            "design_style": design_context.design_style,
            "color_theme": design_context.color_theme,
            "lighting": design_context.lighting,
            "budget": design_context.budget,
        }

        # =====================================================
        # DETECT INTENT
        # =====================================================

        intent = detect_chat_intent(
            message,
            context_data
        )

        print("MESSAGE:", message)
        print("CHAT INTENT:", intent)

        # =====================================================
        # CONVERSATION HISTORY
        # =====================================================

        previous_messages = list(
            ChatMessage.objects.filter(
                conversation=conversation
            )
            .exclude(id=user_message.id)
            .order_by("-created_at")[:10]
        )

        previous_messages.reverse()

        conversation_history = [
            {
                "role": msg.role,
                "content": msg.content
            }
            for msg in previous_messages
            if msg.role in ["user", "assistant"]
        ]

        # =====================================================
        # DEFAULT
        # =====================================================

        ai_response = ""
        room_design = None

        # =====================================================
        # 1. GENERAL AI QUESTION
        # =====================================================

        if intent == "general":

            print("GENERAL QUESTION")

            ai_response = generate_general_response(
                message,
                conversation_history
            )

        # =====================================================
        # 2. WEBSITE / DATABASE QUESTION
        # =====================================================

        elif intent == "database":

            print("DATABASE QUESTION")

            database_context, found = search_website_data(
                message,
                request.user
            )

            if found:

                ai_response = generate_database_response(
                    message,
                    database_context,
                    conversation_history
                )

            else:

                ai_response = (
                    "I couldn't find the requested information "
                    "in the website data."
                )

        # =====================================================
        # 3. INTERIOR DESIGN QUESTION
        # =====================================================

        elif intent == "interior":

            print("INTERIOR DESIGN QUESTION")

            # -------------------------------------------------
            # Extract only for interior questions
            # -------------------------------------------------

            design_data = extract_design_context(message)

            print("EXTRACTED DESIGN DATA:", design_data)

            # -------------------------------------------------
            # Update DesignContext
            # -------------------------------------------------

            for field, value in design_data.items():

                if value is not None:

                    setattr(
                        design_context,
                        field,
                        value
                    )

            design_context.save()

            # -------------------------------------------------
            # Update context_data
            # -------------------------------------------------

            context_data = {
                "room_type": design_context.room_type,
                "room_size": design_context.room_size,
                "design_style": design_context.design_style,
                "color_theme": design_context.color_theme,
                "lighting": design_context.lighting,
                "budget": design_context.budget,
            }

            # -------------------------------------------------
            # Generate interior AI response
            # -------------------------------------------------

            ai_response = generate_ai_response(
                message,
                conversation_history,
                context_data,
                intent=intent
            )

            # -------------------------------------------------
            # Check whether all design information exists
            # -------------------------------------------------

            all_fields_completed = all([
                design_context.room_type,
                design_context.room_size,
                design_context.design_style,
                design_context.color_theme,
                design_context.lighting,
                design_context.budget,
            ])

            print(
                "ALL DESIGN FIELDS COMPLETED:",
                all_fields_completed
            )

            # -------------------------------------------------
            # Generate room design only when complete
            # -------------------------------------------------

            if all_fields_completed:

                design_context.design_plan = ai_response

                design_context.save(
                    update_fields=[
                        "design_plan",
                        "updated_at"
                    ]
                )

                # =============================================
                # GET CLIENT
                # =============================================

                try:

                    client = registermodel.objects.get(
                        id=request.session["log_id"]
                    )

                except registermodel.DoesNotExist:

                    return Response(
                        {
                            "error":
                            "No registered profile found "
                            "for this user."
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # =============================================
                # CREATE / GET ROOM DESIGN
                # =============================================

                room_design, created = (
                    AIRoomDesign.objects.get_or_create(
                        client=client,
                        chat_conversation=conversation,
                        defaults={
                            "room_type":
                                design_context.room_type,

                            "room_size":
                                design_context.room_size,

                            "design_style":
                                design_context.design_style,

                            "color_theme":
                                design_context.color_theme,

                            "lighting":
                                design_context.lighting,

                            "budget":
                                design_context.budget,

                            "prompt": (
                                f"Room size: "
                                f"{design_context.room_size}\n\n"
                                f"{ai_response}"
                            ),

                            "status": "processing",

                            "version": 1,

                            "parent_design": None,
                        }
                    )
                )

                # =============================================
                # BACKUP OLD VERSION
                # =============================================

                if not created and room_design.generated_image:

                    max_version = (
                        room_design.design_versions.aggregate(
                            max_version=Max("version")
                        )["max_version"]
                    )

                    next_version = (
                        max_version or 0
                    ) + 1

                    DesignVersion.objects.create(
                        design=room_design,

                        version=next_version,

                        room_type=room_design.room_type,

                        room_size=(
                            room_design.prompt
                            .split("Room size: ")[1]
                            .split("\n")[0]
                            if room_design.prompt
                            and "Room size: " in room_design.prompt
                            else None
                        ),

                        design_style=(
                            room_design.design_style
                        ),

                        color_theme=(
                            room_design.color_theme
                        ),

                        lighting=(
                            room_design.lighting
                        ),

                        budget=(
                            room_design.budget
                        ),

                        design_plan=(
                            room_design.prompt
                        ),

                        generated_image=(
                            room_design.generated_image
                        ),
                    )

                # =============================================
                # UPDATE CURRENT DESIGN
                # =============================================

                room_design.room_type = (
                    design_context.room_type
                )

                room_design.design_style = (
                    design_context.design_style
                )

                room_design.room_size = (
                    design_context.room_size
                )

                room_design.color_theme = (
                    design_context.color_theme
                )

                room_design.lighting = (
                    design_context.lighting
                )

                room_design.budget = (
                    design_context.budget
                )

                room_design.prompt = (
                    f"Room size: "
                    f"{design_context.room_size}\n\n"
                    f"{ai_response}"
                )

                room_design.status = "processing"

                room_design.save()

                # =============================================
                # GENERATE IMAGE
                # =============================================

                generated_image = generate_room_design(
                    room_design
                )

                image_bytes = base64.b64decode(
                    generated_image
                )

                room_design.generated_image.save(
                    f"room_design_{room_design.id}.png",
                    ContentFile(image_bytes),
                    save=False
                )

                room_design.status = "completed"

                room_design.save()

        elif intent == "modify_design":

            print("MODIFY EXISTING DESIGN")

            # Extract changed design information
            design_data = extract_design_context(message)

            print("MODIFICATION DATA:", design_data)

            # Update only values supplied by the user
            for field, value in design_data.items():

                if value is not None:

                    setattr(
                        design_context,
                        field,
                        value
                    )

            design_context.save()

            # Refresh context
            context_data = {
                "room_type": design_context.room_type,
                "room_size": design_context.room_size,
                "design_style": design_context.design_style,
                "color_theme": design_context.color_theme,
                "lighting": design_context.lighting,
                "budget": design_context.budget,
            }

            print("UPDATED DESIGN CONTEXT:")
            print(context_data)

            # Generate updated design plan
            ai_response = generate_ai_response(
                message,
                conversation_history,
                context_data,
                intent="interior"
            )

            # -----------------------------------------
            # Check complete design
            # -----------------------------------------

            all_fields_completed = all([
                design_context.room_type,
                design_context.room_size,
                design_context.design_style,
                design_context.color_theme,
                design_context.lighting,
                design_context.budget,
            ])

            if all_fields_completed:

                design_context.design_plan = ai_response

                design_context.save(
                    update_fields=[
                        "design_plan",
                        "updated_at"
                    ]
                )

        # Continue with your existing
        # AIRoomDesign / DesignVersion /
        # image generation code
        # =====================================================
        # SAVE ASSISTANT MESSAGE
        # =====================================================

        assistant_message = ChatMessage.objects.create(
            conversation=conversation,
            role="assistant",
            content=ai_response
        )

        # =====================================================
        # RESPONSE
        # =====================================================

        return Response({

            "user_message": {
                "id": user_message.id,
                "content": user_message.content,
                "created_at": user_message.created_at,
            },

            "assistant_message": {
                "id": assistant_message.id,
                "content": assistant_message.content,
                "created_at": assistant_message.created_at,
            },

            "design_context": {
                "room_type": design_context.room_type,
                "room_size": design_context.room_size,
                "design_style": design_context.design_style,
                "color_theme": design_context.color_theme,
                "lighting": design_context.lighting,
                "budget": design_context.budget,
                "design_plan": design_context.design_plan,
            },

            "room_design_id": (
                room_design.id
                if room_design
                else None
            ),

            "result_url": (
                reverse(
                    "ai_room_result",
                    kwargs={
                        "design_id": room_design.id
                    }
                )
                if room_design
                else None
            ),
        })

def chat_page(request):
    return render(request, "chatbot/chat.html")

class ChatConversationMessagesView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, conversation_id):

        try:
            conversation = ChatConversation.objects.get(
                id=conversation_id,
                user=request.user
            )
        except ChatConversation.DoesNotExist:
            return Response(
                {
                    "error": "Conversation does not exist."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        messages = conversation.messages.order_by("created_at")

        serializer = ChatMessageSerializer(
            messages,
            many=True
        )

        return Response(serializer.data)
