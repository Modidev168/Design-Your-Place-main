from django.urls import path
from . import views
from .views import *

urlpatterns = [
    path("conversations/",ChatConversationListCreateView.as_view(),name="conversation-list-create"),
    path("conversations/<int:conversation_id>/message/",SendMessageView.as_view(),name="send-message"),
    path("chat/", views.chat_page, name="chat_page"),
    path("conversations/<int:conversation_id>/messages/",ChatConversationMessagesView.as_view(),name="conversation-messages"),
]
