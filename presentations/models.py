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
        return f"{self.title} - {self.presenter.username}"


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
    guest_name = models.CharField(
        max_length=100,
        blank=True,
        help_text='비회원 댓글 작성자명'
    )

    class Meta:
        ordering = ['-created_at']

    def clean(self):
        """데이터 정리 및 검증"""
        super().clean()

        if self.user:
            # 회원 댓글인 경우: guest_name 비우기
            self.guest_name = ''
        else:
            # 비회원 댓글인 경우: guest_name이 없으면 Anonymous 설정
            if not self.guest_name:
                self.guest_name = 'Anonymous'

    @property
    def author_name(self):
        """작성자명 반환"""
        return self.user.username if self.user else (self.guest_name or 'Anonymous')

    @property
    def is_member_comment(self):
        """회원 댓글 여부"""
        return self.user is not None

    def can_edit(self, user):
        """수정 권한 확인"""
        if not user or not user.is_authenticated:
            return False
        # 회원 댓글만 수정 가능하고, 본인만 수정 가능
        return self.is_member_comment and self.user == user

    def can_delete(self, user):
        """삭제 권한 확인"""
        if not user or not user.is_authenticated:
            return False

        # 어드민은 모든 댓글 삭제 가능
        if hasattr(user, 'user_type') and user.user_type == User.UserType.ADMIN:
            return True

        # 회원 댓글은 본인만 삭제 가능
        return self.is_member_comment and self.user == user

    def save(self, *args, **kwargs):
        # 저장 전에 clean 실행
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        comment_type = "회원" if self.is_member_comment else "비회원"
        return f"[{comment_type}] {self.author_name}: {self.content[:50]}"

"""
발표 등록/수정용 ModelForm은 presentations/forms.py에 구현 예정
"""