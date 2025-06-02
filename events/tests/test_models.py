"""
Event 모델 테스트
Django Styleguide: 모델은 검증, 속성, 메서드가 있을 때만 테스트
"""
import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, time, date, timedelta

from events.models import Event, EventRegistration
from events.tests.factories import (
    EventFactory, EventRegistrationFactory,
    MemberEventRegistrationFactory, GuestEventRegistrationFactory
)
from users.tests.factories import UserFactory


@pytest.mark.django_db
class TestEventModel:
    """Event 모델 테스트"""

    def test_event_creation_with_factory(self):
        """팩토리로 이벤트 생성 테스트"""
        event = EventFactory()

        assert event.id is not None
        assert event.title
        assert event.description
        assert event.event_date
        assert event.start_time
        assert event.end_time
        assert event.location
        assert event.max_participants > 0
        assert event.status == Event.Status.PLANNING
        assert event.created_by
        assert event.created_at is not None
        assert event.updated_at is not None

    def test_event_string_representation(self):
        """__str__ 메서드 테스트"""
        event = EventFactory(
            title="Django 스터디",
            event_date=date(2024, 12, 25)
        )

        expected = "Django 스터디 (2024-12-25)"
        assert str(event) == expected

    def test_event_status_choices(self):
        """이벤트 상태 선택지 테스트"""
        assert Event.Status.PLANNING == 'PLANNING'
        assert Event.Status.IN_PROGRESS == 'IN_PROGRESS'
        assert Event.Status.COMPLETED == 'COMPLETED'
        assert Event.Status.CANCELLED == 'CANCELLED'

    def test_event_ordering(self):
        """이벤트 기본 정렬 테스트"""
        # 다른 날짜와 시간으로 이벤트 생성
        event1 = EventFactory(
            event_date=date(2024, 12, 25),
            start_time=time(19, 0)
        )
        event2 = EventFactory(
            event_date=date(2024, 12, 25),
            start_time=time(18, 0)
        )
        event3 = EventFactory(
            event_date=date(2024, 12, 24),
            start_time=time(19, 0)
        )

        events = Event.objects.all()

        # 최신 날짜, 늦은 시간 순으로 정렬되어야 함
        assert events[0] == event1  # 12/25 19:00
        assert events[1] == event2  # 12/25 18:00
        assert events[2] == event3  # 12/24 19:00

    def test_event_related_name_with_location(self):
        """Location과의 관계 테스트"""
        event = EventFactory()
        location = event.location

        # location.events로 접근 가능해야 함
        assert event in location.events.all()

    def test_event_related_name_with_user(self):
        """User와의 관계 테스트"""
        event = EventFactory()
        user = event.created_by

        # user.created_events로 접근 가능해야 함
        assert event in user.created_events.all()


@pytest.mark.django_db
class TestEventRegistrationModel:
    """EventRegistration 모델 테스트"""

    def test_event_registration_creation_with_factory(self):
        """팩토리로 이벤트 등록 생성 테스트"""
        registration = EventRegistrationFactory()

        assert registration.id is not None
        assert registration.event
        assert registration.name
        assert registration.email
        assert registration.phone
        assert registration.company
        assert registration.how_did_you_know
        assert registration.registered_at is not None

    def test_guest_registration(self):
        """비회원 등록 테스트"""
        registration = GuestEventRegistrationFactory(
            name="김게스트",
            email="guest@example.com"
        )

        assert registration.name == "김게스트"
        assert registration.email == "guest@example.com"
        assert registration.user is None

    def test_member_registration(self):
        """회원 등록 테스트"""
        user = UserFactory(name="김회원", email="member@example.com")
        registration = MemberEventRegistrationFactory(
            user=user,
            name="김회원",
            email="member@example.com"
        )

        assert registration.user == user
        assert registration.name == "김회원"
        assert registration.email == "member@example.com"

    def test_event_registration_string_representation(self):
        """__str__ 메서드 테스트"""
        registration = EventRegistrationFactory(
            name="김테스트",
            event__title="Django 스터디"
        )

        expected = "김테스트 - Django 스터디"
        assert str(registration) == expected

    def test_unique_together_constraint(self):
        """같은 이벤트에 같은 이메일로 중복 등록 방지 테스트"""
        event = EventFactory()
        EventRegistrationFactory(event=event, email="test@example.com")

        # 같은 이벤트에 같은 이메일로 등록 시도
        with pytest.raises(Exception):  # IntegrityError 예상
            EventRegistrationFactory(event=event, email="test@example.com")

    def test_event_registration_ordering(self):
        """등록 기본 정렬 테스트 (최신순)"""
        registration1 = EventRegistrationFactory()
        registration2 = EventRegistrationFactory()
        registration3 = EventRegistrationFactory()

        registrations = EventRegistration.objects.all()

        # 최신 등록이 먼저 와야 함
        assert registrations[0] == registration3
        assert registrations[1] == registration2
        assert registrations[2] == registration1

    def test_event_registration_related_names(self):
        """관계 필드 related_name 테스트"""
        registration = EventRegistrationFactory()
        event = registration.event

        # event.registrations로 접근 가능해야 함
        assert registration in event.registrations.all()

        # 회원 등록인 경우
        if registration.user:
            user = registration.user
            # user.event_registrations로 접근 가능해야 함
            assert registration in user.event_registrations.all()