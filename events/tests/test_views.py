"""
Event ViewSet 테스트
Django Styleguide: API 뷰는 HTTP 메서드별로 테스트
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from events.models import Event, EventRegistration
from events.tests.factories import (
    EventFactory, EventRegistrationFactory,
    PastEventFactory, InProgressEventFactory
)
from users.tests.factories import UserFactory, AdminUserFactory
from locations.tests.factories import LocationFactory


@pytest.mark.django_db
class TestEventViewSet:
    """EventViewSet 테스트"""

    def test_event_list_anonymous_access(self, api_client):
        """비인증 사용자도 이벤트 목록 조회 가능 (IsAuthenticatedOrReadOnly)"""
        EventFactory.create_batch(3)

        url = reverse('event-list')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3

    def test_event_list_authenticated_access(self, authenticated_api_client):
        """인증된 사용자의 이벤트 목록 조회"""
        EventFactory.create_batch(5)

        url = reverse('event-list')
        response = authenticated_api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 5

    def test_event_detail_anonymous_access(self, api_client):
        """비인증 사용자도 이벤트 상세 조회 가능"""
        event = EventFactory(title="Django 컨퍼런스")

        url = reverse('event-detail', kwargs={'pk': event.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == event.id
        assert response.data['title'] == "Django 컨퍼런스"

    def test_event_create_requires_authentication(self, api_client):
        """이벤트 생성은 인증 필요"""
        location = LocationFactory()

        url = reverse('event-list')
        data = {
            'title': '새 이벤트',
            'description': '새 이벤트 설명',
            'event_date': '2024-12-25',
            'start_time': '19:00:00',
            'end_time': '21:00:00',
            'location': location.id,
            'max_participants': 50
        }

        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_event_create_success(self, authenticated_api_client):
        """인증된 사용자의 이벤트 생성 성공"""
        location = LocationFactory()

        url = reverse('event-list')
        data = {
            'title': '새 이벤트',
            'description': '새 이벤트 설명',
            'event_date': '2024-12-25',
            'start_time': '19:00:00',
            'end_time': '21:00:00',
            'location': location.id,
            'max_participants': 50
        }

        response = authenticated_api_client.get('/api/events/')  # ViewSet URL 확인용
        response = authenticated_api_client.post(url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == '새 이벤트'
        assert response.data['description'] == '새 이벤트 설명'

        # created_by가 자동으로 설정되었는지 확인
        event = Event.objects.get(id=response.data['id'])
        assert event.created_by is not None

    def test_event_create_invalid_data(self, authenticated_api_client):
        """잘못된 데이터로 이벤트 생성 실패"""
        url = reverse('event-list')
        data = {
            'title': '',  # 빈 제목
            'description': '설명',
            'event_date': 'invalid-date',  # 잘못된 날짜
            'location': 99999,  # 존재하지 않는 장소
            'max_participants': -10  # 음수
        }

        response = authenticated_api_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'title' in response.data
        assert 'event_date' in response.data
        assert 'location' in response.data

    def test_event_update_requires_authentication(self, api_client):
        """이벤트 수정은 인증 필요"""
        event = EventFactory()

        url = reverse('event-detail', kwargs={'pk': event.id})
        data = {'title': '수정된 제목'}

        response = api_client.patch(url, data)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_event_update_success(self, authenticated_api_client):
        """인증된 사용자의 이벤트 수정 성공"""
        event = EventFactory(title="원래 제목")

        url = reverse('event-detail', kwargs={'pk': event.id})
        data = {'title': '수정된 제목'}

        response = authenticated_api_client.patch(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == '수정된 제목'

    def test_event_delete_requires_authentication(self, api_client):
        """이벤트 삭제는 인증 필요"""
        event = EventFactory()

        url = reverse('event-detail', kwargs={'pk': event.id})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_event_delete_success(self, authenticated_api_client):
        """인증된 사용자의 이벤트 삭제 성공"""
        event = EventFactory()
        event_id = event.id

        url = reverse('event-detail', kwargs={'pk': event.id})
        response = authenticated_api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Event.objects.filter(id=event_id).exists()


@pytest.mark.django_db
class TestEventRegistrationViewSet:
    """EventRegistrationViewSet 테스트"""

    def test_registration_list_anonymous_access(self, api_client):
        """비인증 사용자도 등록 목록 조회 가능"""
        EventRegistrationFactory.create_batch(3)

        url = reverse('eventregistration-list')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3

    def test_registration_detail_anonymous_access(self, api_client):
        """비인증 사용자도 등록 상세 조회 가능"""
        registration = EventRegistrationFactory(name="김테스트")

        url = reverse('eventregistration-detail', kwargs={'pk': registration.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == registration.id
        assert response.data['name'] == "김테스트"

    def test_guest_registration_create_success(self, api_client):
        """비회원 이벤트 등록 실패"""
        event = EventFactory()

        url = reverse('eventregistration-list')
        data = {
            'event': event.id,
            'name': '홍길동',
            'email': 'hong@example.com',
            'phone': '010-1234-5678',
            'company': '테스트 회사',
            'how_did_you_know': '친구 소개'
        }

        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_member_registration_create_success(self, authenticated_api_client, test_user):
        """회원 이벤트 등록 성공"""
        event = EventFactory()

        url = reverse('eventregistration-list')
        data = {
            'event': event.id,
            'name': '김회원',
            'email': 'member@example.com',
            'phone': '010-9999-8888',
            'company': '회원 회사',
            'how_did_you_know': '웹사이트'
        }

        response = authenticated_api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == '김회원'
        assert response.data['user'] == test_user.id  # 회원