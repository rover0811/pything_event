from django.db import models
from django.utils import timezone


class BaseModel(models.Model):
    """
    Django Styleguide 기반 베이스 모델
    """
    created_at = models.DateTimeField(db_index=True, default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
