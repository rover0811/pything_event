from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError


class User(AbstractUser):
    class UserType(models.TextChoices):
        NON_MEMBER = 'non_member', '비회원'
        ASSOCIATE = 'associate', '준회원'
        REGULAR = 'regular', '정회원'
        ADMIN = 'admin', '어드민'
    email = models.EmailField(unique=True)

    username = models.CharField(max_length=100, unique=True)
    phone = models.CharField(max_length=20, blank=True)
    company = models.CharField(max_length=100, blank=True)
    user_type = models.CharField(
        max_length=20,
        choices=UserType.choices,
        default=UserType.NON_MEMBER
    )
    referrer = models.ForeignKey(
        'self', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='referred_users'
    )
    approved_by = models.ForeignKey(
        'self', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='approved_users'
    )
    newsletter_subscribed = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def clean(self):
        """모델 검증 - 간단한 비관계형 필드 검증만"""
        super().clean()
        if self.referrer == self:
            raise ValidationError("자기 자신을 추천인으로 설정할 수 없습니다.")
        if self.approved_by == self:
            raise ValidationError("자기 자신을 승인자로 설정할 수 없습니다.")

    @property
    def is_approved_member(self) -> bool:
        """간단한 파생 값 - 모델 속성으로 적합"""
        return self.user_type == self.UserType.REGULAR

    @property
    def full_display_name(self) -> str:
        """간단한 파생 값"""
        return f"{self.username} ({self.email})"

    def __str__(self):
        return self.full_display_name
