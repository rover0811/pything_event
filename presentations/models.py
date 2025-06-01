from django.db import models
from common.models import BaseModel
from users.models import User

class Presentation(BaseModel):
    title = models.CharField(max_length=200)

    def __str__(self):
        return self.title

class PresentationComment(BaseModel):
    presentation = models.ForeignKey(
        Presentation,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    content = models.TextField()
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='presentation_comments',
        null=True,
        blank=True
    )
    guest_name = models.CharField(max_length=100,default='Anonymous',blank=True)

    class Meta:
        ordering = ['-created_at']

    @property
    def author_name(self):
        return self.user.name if self.user else (self.guest_name or 'Anonymous')

    def __str__(self):
        return f"{self.author_name}: {self.content[:50]}"

