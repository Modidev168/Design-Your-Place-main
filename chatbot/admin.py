from django.contrib import admin
from .models import ChatConversation,ChatMessage
# Register your models here.

@admin.register(ChatConversation)
class ChatConversationAdmin(admin.ModelAdmin):
    list_display = ("id","user","title","created_at","updated_at")
    search_fields = ("title","user")

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ("id","conversation","role","created_at",)
    list_filter = ("role","created_at",)
    search_fields = ("content",)