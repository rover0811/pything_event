from django.db import models
from django.core.exceptions import ValidationError

from common.models import BaseModel


class Locations(BaseModel):
    name = models.CharField(max_length=100, unique=True, verbose_name='장소명')
    address = models.TextField(verbose_name='주소')  # CharField랑 TextField의 차이?
    description = models.TextField(blank=True, verbose_name="장소 설명")
    max_capacity = models.PositiveIntegerField(verbose_name="최대 수용인원")
    objects: 'models.Manager[Locations]' = models.Manager()

    class Meta:  # 얘는 역할이 뭘까?
        verbose_name = "장소"
        verbose_name_plural = "장소들"
        constraints = [
            models.CheckConstraint(
                name="max_capacity_positive",
                check=models.Q(max_capacity__gt=0)
            )
        ]

    def clean(self):
        super().clean()
        if self.max_capacity <= 0:
            raise ValidationError('최대 수용인원은 1명 이상이어야 합니다.')

    @property
    def display_capacity(self) -> str:
        return f"{self.max_capacity}명"

    def __str__(self):
        return self.name
