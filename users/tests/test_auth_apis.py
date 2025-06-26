"""
Auth API 테스트
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

from users.tests.factories import UserFactory

User = get_user_model()


@pytest.mark.django_db
class TestCSRFTokenApi:
    """CSRF 토큰 API 테스트"""

    def test_get_csrf_token(self, api_client):
        """CSRF 토큰 발급 테스트"""
        url = reverse('auth:csrf-token')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert 'csrf_token' in response.data


@pytest.mark.django_db
class TestLoginApi:
    """로그인 API 테스트"""

    def test_login_success(self, api_client):
        """정상 로그인 테스트"""
        user = UserFactory(email='test@example.com')
        user.set_password('testpass123')
        user.save()

        url = reverse('auth:login')
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }

        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['user']['email'] == 'test@example.com'
        assert response.data['user']['name'] == user.name
        assert response.data['message'] == '로그인되었습니다.'

    def test_login_invalid_email(self, api_client):
        """존재하지 않는 이메일로 로그인 실패"""
        url = reverse('auth:login')
        data = {
            'email': 'nonexistent@example.com',
            'password': 'testpass123'
        }

        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert '이메일 또는 비밀번호가 올바르지 않습니다' in response.data['error']

    def test_login_invalid_password(self, api_client):
        """잘못된 비밀번호로 로그인 실패"""
        user = UserFactory(email='test@example.com')
        user.set_password('correctpass')
        user.save()

        url = reverse('auth:login')
        data = {
            'email': 'test@example.com',
            'password': 'wrongpass'
        }

        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_invalid_data(self, api_client):
        """잘못된 입력 데이터 검증"""
        url = reverse('auth:login')
        data = {
            'email': 'invalid-email',  # 잘못된 이메일 형식
            'password': 'testpass123'
        }

        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestLogoutApi:
    """로그아웃 API 테스트"""

    def test_logout_success(self, api_client):
        """정상 로그아웃 테스트"""
        user = UserFactory()
        api_client.force_authenticate(user=user)

        url = reverse('auth:logout')
        response = api_client.post(url)

        assert response.status_code == status.HTTP_200_OK
        assert '로그아웃되었습니다' in response.data['message']

    def test_logout_without_login(self, api_client):
        """로그인하지 않은 상태에서 로그아웃"""
        url = reverse('auth:logout')
        response = api_client.post(url)

        # 로그인하지 않아도 로그아웃은 성공해야 함
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestMeApi:
    """현재 사용자 정보 API 테스트"""

    def test_get_current_user_authenticated(self, api_client):
        """인증된 사용자 정보 조회"""
        user = UserFactory(name='김테스트', email='test@example.com')
        api_client.force_authenticate(user=user)

        url = reverse('auth:me')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == user.id
        assert response.data['email'] == 'test@example.com'
        assert response.data['name'] == '김테스트'
        assert response.data['user_type'] == user.user_type
        assert 'is_approved_member' in response.data

    def test_get_current_user_unauthenticated(self, api_client):
        """인증되지 않은 사용자 정보 조회"""
        url = reverse('auth:me')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert '인증되지 않은 사용자입니다' in response.data['error']


@pytest.mark.django_db
class TestChangePasswordApi:
    """비밀번호 변경 API 테스트"""

    def test_change_password_success(self, api_client):
        """비밀번호 변경 성공"""
        user = UserFactory()
        user.set_password('oldpass123')
        user.save()
        api_client.force_authenticate(user=user)

        url = reverse('auth:change-password')
        data = {
            'current_password': 'oldpass123',
            'new_password': 'newpass123',
            'confirm_password': 'newpass123'
        }

        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert '비밀번호가 변경되었습니다' in response.data['message']

        # 새 비밀번호로 로그인 가능한지 확인
        user.refresh_from_db()
        assert user.check_password('newpass123')

    def test_change_password_wrong_current(self, api_client):
        """현재 비밀번호가 틀린 경우"""
        user = UserFactory()
        user.set_password('correctpass')
        user.save()
        api_client.force_authenticate(user=user)

        url = reverse('auth:change-password')
        data = {
            'current_password': 'wrongpass',
            'new_password': 'newpass123',
            'confirm_password': 'newpass123'
        }

        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert '현재 비밀번호가 올바르지 않습니다' in response.data['error']

    def test_change_password_mismatch(self, api_client):
        """새 비밀번호 확인이 일치하지 않는 경우"""
        user = UserFactory()
        user.set_password('oldpass123')
        user.save()
        api_client.force_authenticate(user=user)

        url = reverse('auth:change-password')
        data = {
            'current_password': 'oldpass123',
            'new_password': 'newpass123',
            'confirm_password': 'differentpass'
        }

        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_change_password_unauthenticated(self, api_client):
        """인증되지 않은 사용자의 비밀번호 변경 시도"""
        url = reverse('auth:change-password')
        data = {
            'current_password': 'oldpass123',
            'new_password': 'newpass123',
            'confirm_password': 'newpass123'
        }

        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestCheckAuthApi:
    """인증 상태 확인 API 테스트"""

    def test_check_auth_authenticated(self, api_client):
        """인증된 사용자 상태 확인"""
        user = UserFactory(name='김테스트')
        api_client.force_authenticate(user=user)

        url = reverse('auth:check')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['authenticated'] is True
        assert response.data['user']['id'] == user.id
        assert response.data['user']['name'] == '김테스트'

    def test_check_auth_unauthenticated(self, api_client):
        """인증되지 않은 사용자 상태 확인"""
        url = reverse('auth:check')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['authenticated'] is False
        assert response.data['user'] is None


# Pytest fixtures
@pytest.fixture
def api_client():
    """API 클라이언트"""
    return APIClient()