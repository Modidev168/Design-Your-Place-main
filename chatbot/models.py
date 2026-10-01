from django.db import models
from django.conf import settings

class ChatConversation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="chat_conversation")
    title = models.CharField(max_length=200,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title or f"Conversation {self.id}"

class ChatMessage(models.Model):
    ROLE_CHOICES = [
        ("user","User"),
        ("assistant","Assistant"),
        ("system","System"),
        ("tool","Tool")
    ]
    # user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="chat_conversation")
    conversation = models.ForeignKey(ChatConversation,on_delete=models.CASCADE,related_name="messages")
    role = models.CharField(max_length=20,choices=ROLE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    content = models.TextField()

    def __str__(self):
        return self.role or self.conversation.id

class DesignContext(models.Model):
    conversation = models.OneToOneField(ChatConversation,on_delete=models.CASCADE,related_name="design_context")
    room_type = models.CharField(max_length=100,blank=True,null=True)
    room_size = models.CharField(max_length=100,blank=True,null=True)
    design_style = models.CharField(max_length=100,blank=True,null=True)
    color_theme = models.CharField(max_length=100,blank=True,null=True)
    lighting = models.CharField(max_length=100,blank=True,null=True)
    budget = models.CharField(max_length=100,blank=True,null=True)
    design_plan = models.TextField(blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Design Context - {self.conversation.id}"