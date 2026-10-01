from groq import Groq
from django.conf import settings
import os
import json
import requests
import re
from myapp.models import (
    registermodel,
    portfolio,
    packages,
    booking,
    contact,
    review,
    AIRoomDesign,
)

# client = Groq(
#     api_key=settings.GROQ_API_KEY
# )
CLOUDFLARE_ACCOUNT_ID = os.getenv(
    "CLOUDFLARE_ACCOUNT_ID"
)

CLOUDFLARE_API_TOKEN = os.getenv(
    "CLOUDFLARE_API_TOKEN"
)

CLOUDFLARE_MODEL = os.getenv(
    "CLOUDFLARE_MODEL",
    "@cf/meta/llama-3.1-8b-fast-v2"
)
SYSTEM_PROMPT = """
You are an AI Interior Designer.

Help users design rooms including bedrooms, living rooms,
kitchens, bathrooms, offices and other spaces.

Use the current design context and conversation history.

Rules:
- Remember information already provided.
- Never ask for information already known.
- Never invent user preferences.
- Extract and use ONLY information explicitly provided by the user.
- Never assume a design style, color, lighting, or budget.
- If a value is missing, treat it as missing.
- Ask ONLY ONE missing question at a time.
- Do NOT explain your reasoning.
- Do NOT describe how you arrived at your answer.
- Do NOT output "final answer", "analysis", "reasoning", "boxed", or similar text.
- Do NOT repeat the user's message.
- Respond directly as an interior designer speaking to the user.

When asking for a preference, provide a few options.
"""
def call_cloudflare(prompt, max_tokens=400):

    url = (
        "https://api.cloudflare.com/client/v4/"
        f"accounts/{CLOUDFLARE_ACCOUNT_ID}/"
        f"ai/run/{CLOUDFLARE_MODEL}"
    )

    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json",
    }

    data = {
        "prompt": prompt,
        "max_tokens": max_tokens,
    }

    response = requests.post(
        url,
        headers=headers,
        json=data,
        timeout=60,
    )

    response.raise_for_status()

    result = response.json()

    if not result.get("success"):
        raise Exception(f"Cloudflare AI error: {result}")

    return result["result"]["response"].strip()

def get_next_design_question(design_context):
    if not design_context.get("room_type"):
        return (
            "What type of room are you designing?\n\n"
            "Options: bedroom, living room, kitchen, bathroom, office."
        )

    if not design_context.get("room_size"):
        return (
            "What is the size of the room?\n\n"
            "For example: 12x14 feet."
        )

    if not design_context.get("design_style"):
        return (
            "What design style would you like?\n\n"
            "Options: modern, minimalist, luxury, Scandinavian, "
            "industrial, traditional, rustic."
        )

    if not design_context.get("color_theme"):
        return (
            "What color theme would you prefer?\n\n"
            "Options: neutral, warm, cool, white, earthy, dark."
        )

    if not design_context.get("lighting"):
        return (
            "What type of lighting would you prefer?\n\n"
            "Options: natural, warm, bright, ambient."
        )

    if not design_context.get("budget"):
        return (
            "What is your approximate budget for this room?\n\n"
            "For example: ₹50,000, ₹1 lakh, or ₹2 lakh."
        )

    return None

def clean_ai_response(response):

    if not response:
        return ""

    response = response.strip()

    # Remove code fences
    response = re.sub(r"```.*?```", "", response, flags=re.DOTALL)

    # Remove /* ... */
    response = re.sub(
        r"/\*.*?\*/",
        "",
        response,
        flags=re.DOTALL
    )

    # Remove triple quotes
    response = response.replace('"""', "")
    response = response.replace("'''", "")

    # Remove USER / ASSISTANT labels
    response = re.sub(
        r"(?im)^\s*(USER|ASSISTANT)\s*:\s*",
        "",
        response
    )

    # Remove model leakage
    response = re.sub(
        r"(?im)^\s*\**Expanded Response\**\s*$",
        "",
        response
    )

    response = re.sub(
        r"(?im)^\s*\**Expanded Response.*$",
        "",
        response
    )

    return response.strip()

# def generate_ai_response(message, conversation_history, design_context=None):

#     design_context = design_context or {}

#     next_question = get_next_design_question(design_context)

#     # Still collecting information
#     if next_question:
#         return next_question

#     # All design information collected
#     context_text = f"""
#     Room Type: {design_context.get("room_type")}
#     Room Size: {design_context.get("room_size")}
#     Design Style: {design_context.get("design_style")}
#     Color Theme: {design_context.get("color_theme")}
#     Lighting: {design_context.get("lighting")}
#     Budget: {design_context.get("budget")}
#     """

#     prompt = f"""
#         You are an AI interior design consultant.

#         Your task is to write a human-readable interior design plan.

#         DESIGN REQUIREMENTS:
#         {context_text}

#         Write the answer directly for the user.

#         Use exactly these sections:

#         1. Design Concept
#         2. Recommended Room Layout
#         3. Furniture Recommendations
#         4. Color Palette
#         5. Lighting Plan
#         6. Flooring Recommendation
#         7. Wall and Ceiling Treatment
#         8. Decor Recommendations
#         9. Budget Allocation
#         10. Final Design Summary

#         STRICT OUTPUT RULES:

#         - Return ONLY the human-readable design plan.
#         - Do NOT write Python code.
#         - Do NOT write JavaScript or any programming language.
#         - Do NOT use variables.
#         - Do NOT use functions.
#         - Do NOT use return statements.
#         - Do NOT use code blocks.
#         - Do NOT use triple quotes.
#         - Do NOT write comments beginning with #.
#         - Do NOT output USER or ASSISTANT.
#         - Do NOT output XML or HTML.
#         - Do NOT output reasoning.
#         - Do NOT ask questions.
#         - Do NOT invent missing requirements.
#         - Respect the exact room dimensions.
#         - Recommend furniture appropriate for the room size.
#         - Keep the recommendations realistic for the specified budget.
#         - Use the specified room type, style, color theme, lighting and budget.
#         - Do not add unrealistic architectural features.
#         - A 12x14 ft room is approximately 168 sq ft.
#         - Keep furniture compact and space-efficient.
#         - Prefer a queen-size bed unless a king-size bed is explicitly requested.
#         - Do not recommend a sofa for this bedroom.
#         - Do not create a separate seating area.
#         - Do not recommend oversized furniture.
#         - Maintain comfortable walking space around the bed and furniture.
#         - Make every recommendation practical for a 168 sq ft bedroom.
#         - Respect the specified budget.
#         - Budget allocation must total exactly 100%.
#         - Show both percentage and approximate INR amount for every budget category.
#         - The budget amounts must add up exactly to the specified total budget.
#         - Complete all 10 sections.
#         - Do not stop before the Final Design Summary.

#         Write a clean professional answer that a homeowner can directly read.
#         """
#     response = call_cloudflare(
#         prompt,
#         max_tokens=1200
#     )

#     return clean_ai_response(response)

def detect_chat_intent(message, design_context=None):
    """
    Decide whether the user wants:
    - interior design
    - website/database information
    - general AI answer
    """

    text = message.lower().strip()
    design_context = design_context or {}

    # ---------------------------------------------------------
    # DATABASE / WEBSITE QUESTIONS
    # ---------------------------------------------------------

    database_keywords = [
        "client",
        "clients",
        "designer",
        "designers",
        "experience",
        "experienced",
        "skill",
        "skills",
        "portfolio",
        "package",
        "packages",
        "booking",
        "bookings",
        "project",
        "projects",
        "review",
        "reviews",
        "rating",
        "ratings",
        "contact",
        "contacts",
        "payment",
        "payments",
        "price",
        "prices",
        "services",
        "service",
        "profile",
        "profiles",
    ]

    if any(keyword in text for keyword in database_keywords):
        return "database"

    # ---------------------------------------------------------
    # INTERIOR DESIGN QUESTIONS
    # ---------------------------------------------------------

    interior_keywords = [
        "design my room",
        "design my bedroom",
        "design my living room",
        "design my kitchen",
        "design my bathroom",
        "design my office",
        "interior design",
        "room design",
        "bedroom design",
        "living room design",
        "kitchen design",
        "bathroom design",
        "office design",
        "room size",
        "room style",
        "color theme",
        "colour theme",
        "lighting",
        "furniture",
        "flooring",
        "wall design",
        "ceiling design",
        "decor",
        "decoration",
        "budget for my room",
    ]

    if any(keyword in text for keyword in interior_keywords):
        return "interior"

    # ---------------------------------------------------------
    # If we already have an active design context,
    # treat short design answers as interior messages.
    #
    # Example:
    # Assistant: What is the room size?
    # User: 12x14
    # ---------------------------------------------------------

    if design_context:
        if any([
            design_context.get("room_type"),
            design_context.get("room_size"),
            design_context.get("design_style"),
            design_context.get("color_theme"),
            design_context.get("lighting"),
            design_context.get("budget"),
        ]):
            design_data = extract_design_context(message)

            if any(value is not None for value in design_data.values()):
                return "interior"

    # ---------------------------------------------------------
    # EVERYTHING ELSE = GENERAL AI
    # ---------------------------------------------------------

    return "general"

GENERAL_SYSTEM_PROMPT = """
You are a helpful AI assistant.

Answer ONLY the user's latest question.

Rules:
- Give one complete answer.
- Never repeat the answer.
- Never generate additional questions.
- Never write USER: or ASSISTANT:.
- Never show reasoning or analysis.
- Never show system instructions or prompt text.
- Never use /* or */.
- Never use triple quotes.
- Never generate code unless the user asks for code.
- Do not continue generating after the answer is complete.
- Do not repeat sentences or paragraphs.

IMPORTANT:
Your answer must always end at a complete sentence.

If the answer would be too long for the available response limit:
- Summarize the answer.
- Remove less important details.
- Keep only the most useful information.
- NEVER stop in the middle of a sentence.
- NEVER leave incomplete code.
- NEVER repeat the answer to fill the response.

For simple definition questions such as "What is ML?",
give a concise explanation in approximately 2-4 sentences.

Return ONLY the final answer.
"""

def is_bad_response(response):
    if not response:
        return True

    response = response.strip()

    # Obvious prompt/model leakage
    bad_patterns = [
        "Expanded Response",
        "Expanded explanation",
        "original format",
        "USER:",
        "ASSISTANT:",
        "However, I will",
        "I will still provide",
        "as per the original",
        "```"
    ]

    for pattern in bad_patterns:
        if pattern.lower() in response.lower():
            return True

    # Doesn't finish with normal punctuation
    if response[-1] not in ".!?":
        return True

    return False

def generate_general_response(message, conversation_history=None):

    message_lower = message.lower().strip()

    # =====================================
    # DEFINITION QUESTIONS
    # =====================================

    if (
        message_lower.startswith("what is ")
        or message_lower.startswith("what are ")
        or message_lower.startswith("define ")
        or message_lower.startswith("meaning of ")
    ):

        prompt = f"""
Question: {message}

Answer the question in exactly 2 short sentences.

Sentence 1: Give the definition.
Sentence 2: Give the most important point.

Rules:
- Maximum 45 words.
- Do not expand the answer.
- Do not repeat anything.
- Do not give examples.
- Do not generate code.
- Do not ask questions.
- Do not write USER or ASSISTANT.
- Do not mention instructions.
- Do not write headings.
- Do not write "Expanded Response".
- Stop immediately after sentence 2.
- Both sentences MUST be complete.

Return only the answer.
"""

        response = call_cloudflare(
            prompt,
            max_tokens=90
        )

        # ---------------------------------
        # RETRY IF MODEL PRODUCES BAD OUTPUT
        # ---------------------------------

        if is_bad_response(response):

            retry_prompt = f"""
Answer this question using ONLY 30-45 words:

{message}

Give exactly TWO complete sentences.

Sentence 1 = definition.
Sentence 2 = important information.

Do NOT add anything else.
Do NOT repeat.
Do NOT expand.
Do NOT ask a question.
Do NOT use headings.
Do NOT use code.
Do NOT write USER or ASSISTANT.

Return only the two sentences.
"""

            response = call_cloudflare(
                retry_prompt,
                max_tokens=75
            )

    # =====================================
    # OTHER QUESTIONS
    # =====================================

    else:

        prompt = f"""
Question:
{message}

Give a complete and concise answer.

Rules:
- Answer only the question.
- Do not repeat information.
- Do not generate additional questions.
- Do not write USER or ASSISTANT.
- Do not mention prompts or instructions.
- Do not continue after the answer is complete.
- Always finish with a complete sentence.
- If the answer is long, summarize it.

Return only the answer.
"""

        response = call_cloudflare(
            prompt,
            max_tokens=300
        )

    return clean_ai_response(response)

def search_website_data(message, user=None):
    """
    Search website/project information from the database.

    Returns:
        context_text
        found
    """

    text = message.lower().strip()

    results = []

    # =========================================================
    # FIND DESIGNER / CLIENT BY NAME
    # =========================================================

    users = registermodel.objects.all()

    # Look for a matching fullname in the question.
    matched_users = []

    for person in users:
        if person.fullname and person.fullname.lower() in text:
            matched_users.append(person)

    # =========================================================
    # PORTFOLIO
    # =========================================================

    portfolios = portfolio.objects.none()

    if matched_users:
        portfolios = portfolio.objects.filter(
            Designerid__in=matched_users
        )

    elif any(word in text for word in [
        "portfolio",
        "experience",
        "skill",
        "skills",
        "designer",
    ]):
        portfolios = portfolio.objects.all()[:10]

    for item in portfolios:
        results.append(
            f"""
            Designer: {item.Designer_Name}
            About: {item.aboutyourself}
            Design Style: {item.designstyle}
            Skills: {item.designerskill}
            Experience: {item.experience}
            """
        )

    # =========================================================
    # PACKAGES
    # =========================================================

    if any(word in text for word in [
        "package",
        "packages",
        "service",
        "services",
        "price",
        "pricing",
    ]):

        if matched_users:
            package_data = packages.objects.filter(
                Designerid__in=matched_users
            )
        else:
            package_data = packages.objects.all()[:10]

        for item in package_data:
            results.append(
                f"""
                Package Designer: {item.Designer_Name}
                Design Style: {item.package_design_style}
                Package Type: {item.package_type}
                Package Category: {item.package_category}
                BHK Type: {item.BhkType}
                Price: ₹{item.package_price}
                Duration: {item.time_duration}
                Description: {item.package_desc}
                Extra Services: {item.ExtraServices}
                """
            )

    # =========================================================
    # BOOKINGS
    # =========================================================

    if any(word in text for word in [
        "booking",
        "bookings",
        "booked",
        "requirement",
        "booking status",
    ]):

        if matched_users:
            booking_data = booking.objects.filter(
                Designerid__in=matched_users
            )
        elif user:
            booking_data = booking.objects.filter(
                client_id=user
            )
        else:
            booking_data = booking.objects.none()

        for item in booking_data[:10]:
            results.append(
                f"""
                Client: {item.Client_Name}
                Design Style: {item.design_style}
                Package Type: {item.package_type}
                Category: {item.package_category}
                BHK Type: {item.BHKType}
                Property Size: {item.propertySize}
                Duration: {item.Time_duration}
                Requirement: {item.requirement}
                Status: {item.status}
                Location: {item.location}
                """
            )

    # =========================================================
    # REVIEWS
    # =========================================================

    if any(word in text for word in [
        "review",
        "reviews",
        "rating",
        "ratings",
    ]):

        review_data = review.objects.all()[:10]

        for item in review_data:
            results.append(
                f"""
                Reviewer: {item.name}
                Rating: {item.star}/5
                Review: {item.review}
                """
            )

    # =========================================================
    # AI ROOM DESIGNS
    # =========================================================

    if any(word in text for word in [
        "previous design",
        "previous designs",
        "ai design",
        "generated design",
        "generated image",
        "room designs",
    ]):

        if matched_users:
            design_data = AIRoomDesign.objects.filter(
                client__in=matched_users
            )
        elif user:
            design_data = AIRoomDesign.objects.filter(
                client=user
            )
        else:
            design_data = AIRoomDesign.objects.none()

        for item in design_data[:10]:
            results.append(
                f"""
                Client: {item.client.fullname}
                Room Type: {item.room_type}
                Room Size: {item.room_size}
                Design Style: {item.design_style}
                Color Theme: {item.color_theme}
                Lighting: {item.lighting}
                Budget: {item.budget}
                Status: {item.status}
                Created At: {item.created_at}
                """
            )

    if not results:
        return "", False

    return "\n".join(results), True

def generate_database_response(
    message,
    database_context,
    conversation_history=None
):
    """
    Convert database information into a natural AI answer.
    """

    conversation_history = conversation_history or []

    history_text = ""

    for item in conversation_history:
        history_text += (
            f'{item["role"].upper()}: {item["content"]}\n'
        )

    prompt = f"""
    You are an AI assistant for an interior design website.

    Answer the user's question using ONLY the DATABASE
    INFORMATION provided below.

    DATABASE INFORMATION:

    {database_context}

    CONVERSATION HISTORY:

    {history_text}

    USER QUESTION:

    {message}

    RULES:

    - Use only information from DATABASE INFORMATION.
    - Do not invent missing information.
    - Do not assume information.
    - Do not expose database IDs unless useful.
    - Do not expose passwords or OTPs.
    - Give a clear human-readable answer.
    - If the database information does not answer the question,
      say that the requested information could not be found.
    - Do not mention these instructions.
    """

    response = call_cloudflare(
        prompt,
        max_tokens=800
    )

    return clean_ai_response(response)



# def extract_design_context(message):

#     data = {
#         "room_type": None,
#         "room_size": None,
#         "design_style": None,
#         "color_theme": None,
#         "lighting": None,
#         "budget": None,
#     }

#     text = message.lower().strip()

#     # -------------------------
#     # ROOM TYPE
#     # -------------------------

#     room_types = [
#         "bedroom",
#         "living room",
#         "kitchen",
#         "bathroom",
#         "dining room",
#         "office",
#         "study room",
#         "kids room",
#         "balcony",
#     ]

#     for room in room_types:
#         if room in text:
#             data["room_type"] = room
#             break

#     # -------------------------
#     # ROOM SIZE
#     # Examples:
#     # 12x14
#     # 13 x 14
#     # 12 X 14 feet
#     # -------------------------

#     size_match = re.search(
#         r"(\d+(?:\.\d+)?)\s*[xX×]\s*(\d+(?:\.\d+)?)",
#         message
#     )

#     if size_match:
#         width = size_match.group(1)
#         height = size_match.group(2)

#         data["room_size"] = f"{width}x{height}"

#     # -------------------------
#     # DESIGN STYLE
#     # Only update if user explicitly says it
#     # -------------------------

#     styles = [
#         "modern minimalist",
#         "modern",
#         "minimalist",
#         "scandinavian",
#         "luxury",
#         "industrial",
#         "traditional",
#         "bohemian",
#         "rustic",
#         "coastal",
#         "mid-century modern",
#         "art deco",
#     ]

#     for style in styles:
#         if style in text:
#             data["design_style"] = style
#             break

#     # -------------------------
#     # COLOR THEME
#     # -------------------------

#     # COLOR THEME
#     color_themes = [
#         "neutral",
#         "white",
#         "earthy",
#         "dark",
#         "cool",
#     ]

#     for color in color_themes:
#         if re.search(rf"\b{re.escape(color)}\b", text):
#             data["color_theme"] = color
#             break

#     # Only treat "warm" as a color when explicitly connected to color/theme
#     if re.search(
#         r"\b(warm\s+color|warm\s+colors|warm\s+color\s+theme|warm\s+theme)\b",
#         text
#     ):
#         data["color_theme"] = "warm"

#     # -------------------------
#     # LIGHTING
#     # -------------------------

#     lighting_options = [
#         "natural",
#         "warm",
#         "bright",
#         "ambient",
#     ]

#     for lighting in lighting_options:
#         if lighting in text:
#             data["lighting"] = lighting
#             break

#     # -------------------------
#     # BUDGET
#     # Examples:
#     # 50000
#     # ₹50,000
#     # 1 lakh
#     # -------------------------

#     budget_match = re.search(
#         r"(?:budget|cost|spend|price|investment)?"
#         r".{0,20}?"
#         r"(?:(?:₹|rs\.?|inr)\s*)?"
#         r"([\d,]+(?:\.\d+)?\s*(?:lakh|lakhs|k)?)",
#         text,
#         re.IGNORECASE
#     )

#     if budget_match:
#         data["budget"] = budget_match.group(1).strip()

#     return data

def generate_ai_response(message, conversation_history, design_context=None):

    design_context = design_context or {}

    # ---------------------------------------------------------
    # CHECK WHICH DESIGN INFORMATION IS STILL MISSING
    # ---------------------------------------------------------

    next_question = get_next_design_question(design_context)

    missing_fields = []

    field_names = {
        "room_type": "Room Type",
        "room_size": "Room Size",
        "design_style": "Design Style",
        "color_theme": "Color Theme",
        "lighting": "Lighting",
        "budget": "Budget",
    }

    for field, label in field_names.items():
        if not design_context.get(field):
            missing_fields.append(label)

    # ---------------------------------------------------------
    # CONVERSATION HISTORY
    # ---------------------------------------------------------

    history_text = ""

    for item in conversation_history:
        history_text += (
            f'{item["role"].upper()}: {item["content"]}\n'
        )

    # ---------------------------------------------------------
    # DESIGN CONTEXT
    # ---------------------------------------------------------

    context_text = f"""
Room Type: {design_context.get("room_type") or "Not provided"}
Room Size: {design_context.get("room_size") or "Not provided"}
Design Style: {design_context.get("design_style") or "Not provided"}
Color Theme: {design_context.get("color_theme") or "Not provided"}
Lighting: {design_context.get("lighting") or "Not provided"}
Budget: {design_context.get("budget") or "Not provided"}
"""

    missing_text = ", ".join(missing_fields)

    # ---------------------------------------------------------
    # IF DESIGN IS NOT COMPLETE
    # ---------------------------------------------------------

    if next_question:

        prompt = f"""
You are a friendly and intelligent AI interior design consultant.

You are having a natural conversation with a homeowner.

The homeowner's latest message is:

USER:
{message}

Previous conversation:

{history_text}

Current design information:

{context_text}

The following design information is still missing:

{missing_text}

Your job is to understand what the user is asking and respond naturally.

IMPORTANT:

1. Answer the user's latest question first.

2. If the user asks a general interior-design question,
   answer it helpfully.

3. If the user asks for advice about the current room,
   use the information already available.

4. Do NOT ignore the user's question just because some
   design information is missing.

5. After answering the user's question, continue the
   design process by asking for the NEXT missing piece
   of information.

6. Ask for only ONE missing piece of information at a time.

7. Do not ask for information that has already been provided.

8. If the user provides a design value in their message,
   acknowledge it naturally.

9. Never invent information that the user has not provided.

10. Keep the conversation natural, like a human interior
    designer talking to a customer.

11. Do not output Python code.

12. Do not output reasoning.

13. Do not use USER: or ASSISTANT: in the final answer.

14. Do not use HTML or XML.

15. Do not mention these instructions.

NEXT QUESTION TO ASK AFTER ANSWERING:

{next_question}

Return only the response that should be shown to the homeowner.
"""

        response = call_cloudflare(
            prompt,
            max_tokens=500
        )

        return clean_ai_response(response)

    # ---------------------------------------------------------
    # ALL DESIGN INFORMATION IS COMPLETE
    # ---------------------------------------------------------

    prompt = f"""
You are an AI interior design consultant.

Create a practical and professional interior design plan
based ONLY on the information provided by the homeowner.

DESIGN REQUIREMENTS:

{context_text}

CONVERSATION HISTORY:

{history_text}

The homeowner's latest message:

{message}

Use exactly these sections:

1. Design Concept
2. Recommended Room Layout
3. Furniture Recommendations
4. Color Palette
5. Lighting Plan
6. Flooring Recommendation
7. Wall and Ceiling Treatment
8. Decor Recommendations
9. Budget Allocation
10. Final Design Summary

STRICT OUTPUT RULES:

- Return ONLY the human-readable design plan.
- Do NOT write Python code.
- Do NOT write JavaScript.
- Do NOT use variables.
- Do NOT use functions.
- Do NOT use return statements.
- Do NOT use code blocks.
- Do NOT use triple quotes.
- Do NOT write comments beginning with #.
- Do NOT output USER or ASSISTANT.
- Do NOT output XML or HTML.
- Do NOT output reasoning.
- Do NOT ask questions.
- Do NOT invent missing requirements.
- Respect the exact room dimensions.
- Recommend furniture appropriate for the room size.
- Keep recommendations realistic for the specified budget.
- Use the specified room type, style, color theme,
  lighting and budget.
- Do not add unrealistic architectural features.
- Keep furniture compact and space-efficient.
- Prefer a queen-size bed unless a king-size bed
  is explicitly requested.
- Do not recommend a sofa for a bedroom.
- Do not create a separate seating area.
- Do not recommend oversized furniture.
- Maintain comfortable walking space.
- Respect the specified budget.
- Budget allocation must total exactly 100%.
- Show percentage and approximate INR amount
  for every budget category.
- Budget amounts must add up exactly to the
  specified total budget.
- Complete all 10 sections.
- Do not stop before the Final Design Summary.

Return a clean professional answer that a homeowner
can directly read.
"""

    response = call_cloudflare(
        prompt,
        max_tokens=1200
    )

    return clean_ai_response(response)

def extract_design_context(message):

    data = {
        "room_type": None,
        "room_size": None,
        "design_style": None,
        "color_theme": None,
        "lighting": None,
        "budget": None,
    }

    text = message.lower().strip()

    # =========================================================
    # ROOM TYPE
    # =========================================================

    room_types = [
        "living room",
        "dining room",
        "study room",
        "kids room",
        "bedroom",
        "kitchen",
        "bathroom",
        "office",
        "balcony",
    ]

    for room in room_types:
        if re.search(rf"\b{re.escape(room)}\b", text):
            data["room_type"] = room
            break

    # =========================================================
    # ROOM SIZE
    # Examples:
    # 12x14
    # 12 x 14
    # 12 X 14 feet
    # 12×14 ft
    # =========================================================

    # ROOM SIZE
    # ---------------------------------------------------------

    # First check whether the user is changing the room size.
    # Example:
    # "change 13 x 14 to 12 x 13"
    # We want 12x13, not 13x14.

    change_size_match = re.search(
        r"(?:change|replace|update|modify)"
        r".*?"
        r"(?:to|into)"
        r"\s*"
        r"(\d+(?:\.\d+)?)\s*[x×]\s*(\d+(?:\.\d+)?)",
        text
    )

    if change_size_match:
        width = change_size_match.group(1)
        height = change_size_match.group(2)

        data["room_size"] = f"{width}x{height}"

    else:
        # Normal room-size input
        # Example:
        # "13 x 14"
        # "12x13"
        # "I want a 12x13 bedroom"

        size_match = re.search(
            r"\b(\d+(?:\.\d+)?)\s*[x×]\s*(\d+(?:\.\d+)?)\b",
            text
        )

        if size_match:
            width = size_match.group(1)
            height = size_match.group(2)

            data["room_size"] = f"{width}x{height}"

    # =========================================================
    # DESIGN STYLE
    # =========================================================

    styles = [
        "mid-century modern",
        "modern minimalist",
        "scandinavian",
        "minimalist",
        "industrial",
        "traditional",
        "bohemian",
        "rustic",
        "coastal",
        "art deco",
        "luxury",
        "modern",
    ]

    for style in styles:
        if re.search(rf"\b{re.escape(style)}\b", text):
            data["design_style"] = style
            break

    # =========================================================
    # COLOR THEME
    # =========================================================

    color_themes = [
        "neutral",
        "white",
        "earthy",
        "dark",
        "cool",
    ]

    for color in color_themes:
        if re.search(rf"\b{re.escape(color)}\b", text):
            data["color_theme"] = color
            break

    # Warm color/theme
    if re.search(
        r"\bwarm\s+(?:color|colors|colour|colours|theme)\b",
        text
    ):
        data["color_theme"] = "warm"

    # =========================================================
    # LIGHTING
    # =========================================================

    lighting_options = [
        "natural",
        "warm",
        "bright",
        "ambient",
    ]

    for lighting in lighting_options:
        if re.search(rf"\b{re.escape(lighting)}\b", text):
            data["lighting"] = lighting
            break

    # =========================================================
    # BUDGET
    # =========================================================
    #
    # Supported examples:
    #
    # 1.5 lakh
    # 1.5 lakhs
    # 1.5 lac
    # 1.5 lacs
    # 1.5L
    # ₹1.5 lakh
    # Rs 1.5 lakh
    # INR 1.5 lakh
    # 150000
    # 1,50,000
    # ₹50,000
    # 50k
    # 50 K
    #
    # Also:
    # my budget is 1.5 lakh
    # budget 1.5 lakh
    # I can spend 1.5 lakh
    # around 2 lakh
    # =========================================================
    # BUDGET
    # ---------------------------------------------------------
# -------------------------
# BUDGET
# -------------------------

# First check explicit budget-change messages
    budget_change_match = re.search(
        r"(?:budget|spend|cost|price|investment)"
        r"\s*(?:is|of|to|around|about|approximately|approx)?\s*"
        r"(?:₹|rs\.?|inr)?\s*"
        r"(\d+(?:,\d{2,3})*(?:\.\d+)?)"
        r"\s*"
        r"(lakh(?:s)?|lac(?:s)?|l|k)?\b",
        text,
        re.IGNORECASE
    )

    if budget_change_match:

        number = budget_change_match.group(1).replace(",", "")
        unit = budget_change_match.group(2)

        if unit:
            unit = unit.lower()

            if unit in ["lakh", "lakhs", "lac", "lacs", "l"]:
                data["budget"] = f"{number} lakh"

            elif unit == "k":
                data["budget"] = f"{number}k"

        else:
            data["budget"] = number

    else:

        # Normal budget input such as:
        # 1 lakh
        # 2 lakh
        # ₹50,000
        # 50000
        # 50k

        budget_match = re.search(
            r"(?:₹|rs\.?|inr)?\s*"
            r"(\d+(?:,\d{2,3})*(?:\.\d+)?)"
            r"\s*"
            r"(lakh(?:s)?|lac(?:s)?|l|k)?\b",
            text,
            re.IGNORECASE
        )

        if budget_match:

            number = budget_match.group(1).replace(",", "")
            unit = budget_match.group(2)

            if unit:
                unit = unit.lower()

                if unit in ["lakh", "lakhs", "lac", "lacs", "l"]:
                    data["budget"] = f"{number} lakh"

                elif unit == "k":
                    data["budget"] = f"{number}k"

            else:
                # A plain number is treated as budget
                # when the entire message is just that number.
                if re.fullmatch(
                    r"(?:₹|rs\.?|inr)?\s*"
                    r"\d+(?:,\d{2,3})*(?:\.\d+)?",
                    text,
                    re.IGNORECASE
                ):
                    data["budget"] = number
    return data   
