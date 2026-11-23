# chat/urls.py
from django.urls import path
from .views import ChatAskView, ChatHistoryView

urlpatterns = [
    path("ask/", ChatAskView.as_view(), name="chat-ask"),
    path("history/<int:file_id>/", ChatHistoryView.as_view(), name="chat-history"),
]
