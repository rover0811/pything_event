"""
Event 시리얼라이저 테스트
Django Styleguide: 시리얼라이저는 유효성 검사와 직렬화/역직렬화를 테스트
"""
import pytest
from datetime import date, time
from django.utils import timezone

from events.serializers import EventSerializer, EventRegistrationSerializer
from events.tests.factories import EventFactory, EventRegistrationFactory
from users.tests.factories import UserFactory
from locations.tests.factories import LocationFactory


@pytest.mark.django_db
class TestEventSerializer:
    """EventSerializer 테스트"""

    def test_event_serialization(self):
        """이벤트 직렬화 테스트"""
        event = EventFactory(
            title="Django 컨퍼런스",
            description="Django 관련 컨퍼런스입니다",
            max_participants=100
        )

        serializer = EventSerializer(event)
        data = serializer.data

        assert data['id'] == event.id
        assert data['title'] == "Django 컨퍼런스"
        assert data['description'] == "Django 관련 컨퍼런스입니다"
        assert data['max_participants'] == 100
        assert data['status'] == event.status
        assert data['location'] == event.location.id
        assert data['created_by'] == event.created_by.id
        assert 'created_at' in data
        assert 'updated_at' in data

    def test_event_deserialization_valid_data(self):
        """유효한 데이터로 이벤트 역직렬화 테스트"""
        location = LocationFactory()
        user = UserFactory()

        data = {
            'title': '새로운 이벤트',
            'description': '이벤트 설명',
            'event_date': '2024-12-25',
            'start_time': '19:00:00',
            'end_time': '21:00:00',
            'location': location.id,
            'max_participants': 50,
            'status': 'PLANNING'
        }

        serializer = EventSerializer(data=data)
        assert serializer.is_valid()

        validated_data = serializer.validated_data
        assert validated_data['title'] == '새로운 이벤트'
        assert validated_data['description'] == '이벤트 설명'
        assert validated_data['max_participants'] == 50

    def test_event_deserialization_invalid_data(self):
        """잘못된 데이터로 이벤트 역직렬화 실패 테스트"""
        data = {
            'title': '',  # 빈 제목
            'description': '이벤트 설명',
            'event_date': 'invalid-date',  # 잘못된 날짜 형식
            'start_time': '25:00:00',  # 잘못된 시간
            'end_time': '21:00:00',
            'location': 99999,  # 존재하지 않는 장소
            'max_participants': -10,  # 음수
        }

        serializer = EventSerializer(data=data)
        assert not serializer.is_valid()

        # 오류 필드 확인
        assert 'title' in serializer.errors
        assert 'event_date' in serializer.errors
        assert 'start_time' in serializer.errors
        assert 'location' in serializer.errors
        assert 'max_participants' in serializer.errors

    def test_event_read_only_fields(self):
        """읽기 전용 필드 테스트"""
        location = LocationFactory()
        user = UserFactory()

        data = {
            'title': '새로운 이벤트',
            'description': '이벤트 설명',
            'event_date': '2024-12-25',
            'start_time': '19:00:00',
            'end_time': '21:00:00',
            'location': location.id,
            'max_participants': 50,
            'created_by': user.id,  # 읽기 전용 필드
            'created_at': '2024-01-01T00:00:00Z',  # 읽기 전용 필드
            'updated_at': '2024-01-01T00:00:00Z',  # 읽기 전용 필드
        }

        serializer = EventSerializer(data=data)
        assert serializer.is_valid()

        # 읽기 전용 필드는 validated_data에 포함되지 않아야 함
        assert 'created_by' not in serializer.validated_data
        assert 'created_at' not in serializer.validated_data
        assert 'updated_at' not in serializer.validated_data


@pytest.mark.django_db
class TestEventRegistrationSerializer:
    """EventRegistrationSerializer 테스트"""

    def test_event_registration_serialization(self):
        """이벤트 등록 직렬화 테스트"""
        registration = EventRegistrationFactory(
            name="김테스트",
            email="test@example.com",
            phone="010-1234-5678",
            company="테스트 회사"
        )

        serializer = EventRegistrationSerializer(registration)
        data = serializer.data

        assert data['id'] == registration.id
        assert data['name'] == "김테스트"
        assert data['email'] == "test@example.com"
        assert data['phone'] == "010-1234-5678"
        assert data['company'] == "테스트 회사"
        assert data['event'] == registration.event.id
        assert 'registered_at' in data
        assert 'user' in data

    def test_guest_registration_deserialization(self):
        """비회원 등록 역직렬화 테스트"""
        event = EventFactory()

        data = {
            'event': event.id,
            'name': '김게스트',
            'email': 'guest@example.com',
            'phone': '010-9999-8888',
            'company': '게스트 회사',
            'how_did_you_know': '친구 소개'
        }

        serializer = EventRegistrationSerializer(data=data)
        assert serializer.is_valid()

        validated_data = serializer.validated_data
        assert validated_data['name'] == '김게스트'
        assert validated_data['email'] == 'guest@example.com'
        assert validated_data['how_did_you_know'] == '친구 소개'

    def test_event_registration_deserialization_invalid_data(self):
        """잘못된 데이터로 등록 역직렬화 실패 테스트"""
        data = {
            'event': 99999,  # 존재하지 않는 이벤트
            'name': '',  # 빈 이름
            'email': 'invalid-email',  # 잘못된 이메일 형식
            'phone': '',  # 빈 전화번호
            'company': '',  # 빈 회사명
            'how_did_you_know': ''  # 빈 소개 경로
        }

        serializer = EventRegistrationSerializer(data=data)
        assert not serializer.is_valid()

        # 오류 필드 확인
        assert 'event' in serializer.errors
        assert 'name' in serializer.errors
        assert 'email' in serializer.errors

    def test_event_registration_read_only_fields(self):
        """읽기 전용 필드 테스트"""
        event = EventFactory()
        user = UserFactory()

        data = {
            'event': event.id,
            'name': '김테스트',
            'email': 'test@example.com',
            'phone': '010-1234-5678',
            'company': '테스트 회사',
            'how_did_you_know': '웹사이트',
            'registered_at': '2024-01-01T00:00:00Z',  # 읽기 전용 필드
            'user': user.id,  # 읽기 전용 필드
        }

        serializer = EventRegistrationSerializer(data=data)
        assert serializer.is_valid()

        # 읽기 전용 필드는 validated_data에 포함되지 않아야 함
        assert 'registered_at' not in serializer.validated_data
        assert 'user' not in serializer.validated_data

    def test_required_fields_validation(self):
        """필수 필드 유효성 검사 테스트"""
        # 모든 필수 필드가 누락된 경우
        data = {}

        serializer = EventRegistrationSerializer(data=data)
        assert not serializer.is_valid()

        # 필수 필드들이 오류에 포함되어야 함
        required_fields = ['event', 'name', 'email', 'phone', 'company', 'how_did_you_know']
        for field in required_fields:
            assert field in serializer.errors