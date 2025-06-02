import factory
from factory.django import DjangoModelFactory
from django.utils import timezone
from datetime import datetime, time, date, timedelta

from events.models import Event, EventRegistration
from users.tests.factories import UserFactory
from locations.tests.factories import LocationFactory


class EventFactory(DjangoModelFactory):
    class Meta:
        model = Event

    title = factory.Sequence(lambda n: f"테스트 이벤트 {n}")
    description = factory.Faker('text', max_nb_chars=500, locale='ko_KR')
    event_date = factory.LazyFunction(lambda: (timezone.now() + timedelta(days=7)).date())
    start_time = time(19, 0)  # 오후 7시
    end_time = time(21, 0)   # 오후 9시
    location = factory.SubFactory(LocationFactory)
    max_participants = factory.Faker('random_int', min=10, max=100)
    status = Event.Status.PLANNING
    created_by = factory.SubFactory(UserFactory)


class PastEventFactory(EventFactory):
    """과거 이벤트 팩토리"""
    event_date = factory.LazyFunction(lambda: (timezone.now() - timedelta(days=7)).date())
    status = Event.Status.COMPLETED


class InProgressEventFactory(EventFactory):
    """진행중 이벤트 팩토리"""
    event_date = factory.LazyFunction(lambda: timezone.now().date())
    status = Event.Status.IN_PROGRESS


class CancelledEventFactory(EventFactory):
    """취소된 이벤트 팩토리"""
    status = Event.Status.CANCELLED


class EventRegistrationFactory(DjangoModelFactory):
    class Meta:
        model = EventRegistration

    event = factory.SubFactory(EventFactory)
    name = factory.Faker('name', locale='ko_KR')
    email = factory.Faker('email')
    phone = factory.Faker('phone_number', locale='ko_KR')
    company = factory.Faker('company', locale='ko_KR')
    how_did_you_know = factory.Faker('sentence', locale='ko_KR')


class MemberEventRegistrationFactory(EventRegistrationFactory):
    """회원 이벤트 등록 팩토리"""
    user = factory.SubFactory(UserFactory)


class GuestEventRegistrationFactory(EventRegistrationFactory):
    """비회원 이벤트 등록 팩토리"""
    user = None