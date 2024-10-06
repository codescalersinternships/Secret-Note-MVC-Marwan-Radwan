import uuid
from django.db import models


class Note(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content = models.TextField()
    remaining_views = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    expire_at = models.DateTimeField()
