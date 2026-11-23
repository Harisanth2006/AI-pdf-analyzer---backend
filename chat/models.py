from django.db import models

# Create your models here.
# chat/models.py
from django.conf import settings
from django.db import models
from document.models import Document

class ChatMessage(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chat_messages",
    )
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="chat_messages",
    )
    question = models.TextField()
    answer = models.TextField()
    order_number = models.PositiveIntegerField(editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order_number"]  # Always returns messages in exact conversation order

    def save(self, *args, **kwargs):
        # Auto-assign the next order_number for this specific user + document chat
        if not self.pk:
            last_msg = (
                ChatMessage.objects.filter(user=self.user, document=self.document)
                .order_by("-order_number")
                .first()
            )
            self.order_number = (last_msg.order_number + 1) if last_msg else 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Doc {self.document_id} | #{self.order_number}: {self.question[:30]}"
