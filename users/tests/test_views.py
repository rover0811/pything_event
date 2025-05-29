"""
API 뷰 테스트
Django Styleguide: API 뷰는 HTTP 메서드별로 테스트
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from users.tests.factories import UserFactory, AdminUserFactory


@pytest.mark.django_db
class TestUserCreateApi:
    """사용자 생성 API 테스트"""

    def test_create_user_success(self):
        """사용자 생성 성공 테스트"""
        client = APIClient()
        url = reverse('api:users:create')
        data = {
            'email': 'test@example.com',
            'name': '테스트',
            'password': 'testpass123',
            'phone': '010-1234-5678',
            'company': '테스트 회사',
            'newsletter_subscribed': True
        }

        response = client.post(url, data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['email'] == data['email']
        assert response.data['name'] == data['name']
        assert 'id' in response.data
        assert 'date_joined' in response.data

    def test_create_user_with_invalid_data(self):
        """잘못된 데이터로 사용자 생성 실패 테스트"""
        client = APIClient()
        url = reverse('api:users:create')
        data = {
            'email': 'invalid-email',
            'name': '테스트',
            'password': '123'  # 너무 짧은 비밀번호
        }

        response = client.post(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data
        assert 'password' in response.data


@pytest.mark.django_db
class TestUserListApi:
    """사용자 목록 API 테스트"""

    def test_list_users_requires_authentication(self):
        """인증 필요 테스트"""
        client = APIClient()
        url = reverse('api:users:list')

        response = client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_users_success(self):
        """사용자 목록 조회 성공 테스트"""
        client = APIClient()
        user = UserFactory()
        client.force_authenticate(user=user)
        url = reverse('api:users:list')

        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)

    def test_list_users_with_filters(self):
        """필터 적용 테스트"""
        client = APIClient()
        user = UserFactory()
        client.force_authenticate(user=user)
        url = reverse('api:users:list')
        
        # 필터 파라미터 추가
        url += '?user_type=NON_MEMBER&newsletter_subscribed=true'

        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)


@pytest.mark.django_db
class TestUserDetailApi:
    """사용자 상세 조회 API 테스트"""

    def test_get_user_detail_requires_authentication(self):
        """인증 필요 테스트"""
        client = APIClient()
        user = UserFactory()
        url = reverse('api:users:detail', kwargs={'user_id': user.id})

        response = client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_user_detail_success(self):
        """사용자 상세 조회 성공 테스트"""
        client = APIClient()
        user = UserFactory()
        client.force_authenticate(user=user)
        url = reverse('api:users:detail', kwargs={'user_id': user.id})

        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == user.id
        assert response.data['email'] == user.email
        assert response.data['name'] == user.name


@pytest.mark.django_db
class TestUserUpdateApi:
    """사용자 정보 수정 API 테스트"""

    def test_update_user_requires_authentication(self):
        """인증 필요 테스트"""
        client = APIClient()
        user = UserFactory()
        url = reverse('api:users:update', kwargs={'user_id': user.id})
        data = {'name': '새이름'}

        response = client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_own_user_success(self):
        """자신의 정보 수정 성공 테스트"""
        client = APIClient()
        user = UserFactory()
        client.force_authenticate(user=user)
        url = reverse('api:users:update', kwargs={'user_id': user.id})
        data = {
            'name': '새이름',
            'phone': '010-9999-8888',
            'company': '새회사'
        }

        response = client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == data['name']
        assert response.data['phone'] == data['phone']
        assert response.data['company'] == data['company']

    def test_update_other_user_forbidden(self):
        """다른 사용자 정보 수정 실패 테스트"""
        client = APIClient()
        user1 = UserFactory()
        user2 = UserFactory()
        client.force_authenticate(user=user1)
        url = reverse('api:users:update', kwargs={'user_id': user2.id})
        data = {'name': '새이름'}

        response = client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestUserApproveApi:
    """사용자 승인 API 테스트"""

    def test_approve_user_requires_admin(self):
        """어드민 권한 필요 테스트"""
        client = APIClient()
        user = UserFactory()
        admin = AdminUserFactory()
        client.force_authenticate(user=user)
        url = reverse('api:users:approve', kwargs={'user_id': admin.id})

        response = client.post(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_approve_user_success(self):
        """사용자 승인 성공 테스트"""
        client = APIClient()
        admin = AdminUserFactory()
        user = UserFactory()
        client.force_authenticate(user=admin)
        url = reverse('api:users:approve', kwargs={'user_id': user.id})

        response = client.post(url)

        assert response.status_code == status.HTTP_200_OK
        assert 'message' in response.data
        assert response.data['approved_by_name'] == admin.name


@pytest.mark.django_db
class TestUserPendingApprovalListApi:
    """승인 대기 사용자 목록 API 테스트"""

    def test_pending_approval_list_requires_admin(self):
        """어드민 권한 필요 테스트"""
        client = APIClient()
        user = UserFactory()
        client.force_authenticate(user=user)
        url = reverse('api:users:pending-approval-list')

        response = client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_pending_approval_list_success(self):
        """승인 대기 목록 조회 성공 테스트"""
        client = APIClient()
        admin = AdminUserFactory()
        client.force_authenticate(user=admin)
        url = reverse('api:users:pending-approval-list')

        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list) 