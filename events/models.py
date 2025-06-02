from django.db import models
from django.utils.translation import gettext_lazy as _
from users.models import User
from locations.models import Location


class Event(models.Model):
    class Status(models.TextChoices):
        PLANNING = 'PLANNING', _('계획중')
        IN_PROGRESS = 'IN_PROGRESS', _('진행중')
        COMPLETED = 'COMPLETED', _('완료됨')
        CANCELLED = 'CANCELLED', _('취소됨')

    title = models.CharField(_('제목'), max_length=200)
    description = models.TextField(_('설명'))
    event_date = models.DateField(_('이벤트 날짜'))
    start_time = models.TimeField(_('시작 시간'))
    end_time = models.TimeField(_('종료 시간'))
    location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        verbose_name=_('장소'),
        related_name='events'
    )
    max_participants = models.PositiveIntegerField(_('최대 참석자 수'))
    status = models.CharField(
        _('상태'),
        max_length=20,
        choices=Status.choices,
        default=Status.PLANNING
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name=_('생성자'),
        related_name='created_events'
    )
    created_at = models.DateTimeField(_('생성일'), auto_now_add=True)
    updated_at = models.DateTimeField(_('수정일'), auto_now=True)

    class Meta:
        verbose_name = _('이벤트')
        verbose_name_plural = _('이벤트')
        ordering = ['-event_date', '-start_time']

    def __str__(self):
        return f"{self.title} ({self.event_date})"


class EventRegistration(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        verbose_name=_('이벤트'),
        related_name='registrations'
    )
    name = models.CharField(_('이름'), max_length=100)
    email = models.EmailField(_('이메일'))
    phone = models.CharField(_('전화번호'), max_length=20)
    company = models.CharField(_('회사'), max_length=100)
    how_did_you_know = models.TextField(_('이벤트를 어떻게 알게 되었는지'))
    registered_at = models.DateTimeField(_('등록일'), auto_now_add=True)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('회원'),
        related_name='event_registrations'
    )

    class Meta:
        verbose_name = _('이벤트 등록')
        verbose_name_plural = _('이벤트 등록')
        ordering = ['-registered_at']
        unique_together = ['event', 'email']

    def __str__(self):
        return f"{self.name} - {self.event.title}"
