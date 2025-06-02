from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.utils.translation import gettext_lazy as _
from pathlib import Path

from common.models import BaseModel
from users.models import User
from events.models import Event


def validate_file_size(value):
    """파일 크기 검증 (50MB 제한)"""
    limit = 50 * 1024 * 1024  # 50MB
    if value.size > limit:
        raise ValidationError('파일 크기는 50MB를 초과할 수 없습니다.')

def presentation_upload_to(instance, filename):
    """발표 자료 업로드 경로"""
    # Django가 자동으로 파일명 중복 처리
    return f'presentations/{instance.created_at.year}/user_{instance.presenter.id}/{filename}'


class Presentation(BaseModel):
    class Status(models.TextChoices):
        SUBMITTED = 'submitted', _('신청됨')
        SELECTED = 'selected', _('선정됨')
        COMPLETED = 'completed', _('완료됨')
        REJECTED = 'rejected', _('거절됨')

    title = models.CharField(_('발표 제목'), max_length=200)
    description = models.TextField(_('발표 내용 설명'))

    content_md = models.TextField(
        _('마크다운 내용'),
        blank=True,
        help_text='발표 상세 내용을 마크다운으로 작성하세요'
    )
    file_url = models.FileField(
        _('발표 자료'),
        upload_to=presentation_upload_to,
        validators=[
            FileExtensionValidator(allowed_extensions=['pdf', 'ppt', 'pptx']),
            validate_file_size,
        ],
        null=True,
        blank=True,
        help_text='PDF, PPT, PPTX 파일 업로드 (최대 50MB)'
    )
    status = models.CharField(
        _('상태'),
        max_length=20,
        choices=Status.choices,
        default=Status.SUBMITTED
    )
    selected_for_newsletter = models.BooleanField(
        _('뉴스레터 포함 여부'),
        default=False,
        help_text='이 발표를 뉴스레터에 포함할지 여부'
    )

    # 관계 필드
    presenter = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name=_('발표자'),
        related_name='presentations'
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        verbose_name=_('이벤트'),
        related_name='presentations'
    )

    class Meta:
        verbose_name = _('발표')
        verbose_name_plural = _('발표')
        ordering = ['-created_at']

    def clean(self):
        """모델 검증"""
        super().clean()

        # 정회원만 발표 신청 가능
        if self.presenter and self.presenter.user_type != User.UserType.REGULAR:
            raise ValidationError('정회원만 발표를 신청할 수 있습니다.')

    @property
    def file_name(self) -> str:
        """업로드된 파일명"""
        if self.file_url:
            return Path(self.file_url.name).name
        return ""

    @property
    def file_size_mb(self) -> float:
        """파일 크기 (MB)"""
        if self.file_url:
            try:
                return round(self.file_url.size / (1024 * 1024), 2)
            except (AttributeError, OSError):
                return 0.0
        return 0.0

    def __str__(self):
        return f"{self.title} - {self.presenter.name}"


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
    guest_name = models.CharField(max_length=100, default='Anonymous', blank=True)

    class Meta:
        ordering = ['-created_at']

    @property
    def author_name(self):
        return self.user.name if self.user else (self.guest_name or 'Anonymous')

    def __str__(self):
        return f"{self.author_name}: {self.content[:50]}"
