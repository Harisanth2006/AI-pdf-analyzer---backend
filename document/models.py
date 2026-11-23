from django.db import models

# Create your models here.
# document/models.py
from django.conf import settings
from django.db import models

class Document(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="documents",
    )
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to="pdfs/")  # Saves to media/pdfs/ and stores path
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id} - {self.name} (User {self.user_id})"
