"""
Location API 테스트
Django Styleguide: API는 인터페이스만 테스트, 복잡한 로직은 서비스 테스트에서 커버
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from locations.tests.factories import LocationFactory, SmallLocationFactory, LargeLocationFactory
from users.tests.factories import UserFactory, AdminUserFactory
from locations.models import Location


@pytest.mark.django_db
class TestLocationCreateApi:
    """LocationCreateApi 테스트"""

    def test_location_create_requires_admin(self, api_client):
        """어드민 권한 필요"""
        regular_user = UserFactory()
        api_client.force_authenticate(user=regular_user)

        url = reverse('locations:create')
        data = {
            'name': '테스트장소',
            'address': '테스트주소',
            'max_capacity': 50
        }

        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert '어드민 권한이 필요합니다' in response.data['error']

    def test_location_create_success(self, api_client):
        """정상적인 장소 생성"""
        admin = AdminUserFactory()
        api_client.force_authenticate(user=admin)

        url = reverse('locations:create')
        data = {
            'name': '마루180',
            'address': '서울특별시 강남구 테헤란로 123',
            'max_capacity': 180,
            'description': '개발자 커뮤니티 공간'
        }

        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == '마루180'
        assert response.data['max_capacity'] == 180
        assert response.data['display_capacity'] == '180명'
        assert Location.objects.filter(name='마루180').exists()

    def test_location_create_invalid_data(self, api_client):
        """잘못된 데이터로 장소 생성 실패"""
        admin = AdminUserFactory()
        api_client.force_authenticate(user=admin)

        url = reverse('locations:create')
        data = {
            'name': '',  # 빈 이름
            'address': '테스트주소',
            'max_capacity': 0  # 잘못된 수용인원
        }

        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_location_create_duplicate_name(self, api_client):
        """중복 이름으로 장소 생성 실패"""
        admin = AdminUserFactory()
        api_client.force_authenticate(user=admin)
        LocationFactory(name='기존장소')

        url = reverse('locations:create')
        data = {
            'name': '기존장소',
            'address': '테스트주소',
            'max_capacity': 50
        }

        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert '이미 존재합니다' in str(response.data)


@pytest.mark.django_db
class TestLocationListApi:
    """LocationListApi 테스트"""

    def test_location_list_requires_authentication(self, api_client):
        """인증이 필요한 API"""
        url = reverse('locations:list')

        response = api_client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_location_list_success(self, authenticated_api_client):
        """정상적인 장소 목록 조회"""
        LocationFactory.create_batch(3)

        url = reverse('locations:list')
        response = authenticated_api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3

    def test_location_list_with_search_filter(self, authenticated_api_client):
        """검색 필터가 적용된 장소 목록 조회"""
        LocationFactory(name='마루180')
        LocationFactory(name='마루360')
        LocationFactory(name='회의실A')

        url = reverse('locations:list')
        response = authenticated_api_client.get(url, {'search': '마루'})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_location_list_with_capacity_filter(self, authenticated_api_client):
        """수용인원 필터가 적용된 장소 목록 조회"""
        SmallLocationFactory(max_capacity=30)
        SmallLocationFactory(max_capacity=40)
        LargeLocationFactory(max_capacity=150)

        url = reverse('locations:list')
        response = authenticated_api_client.get(url, {'min_capacity': 50})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['max_capacity'] == 150


@pytest.mark.django_db
class TestLocationDetailApi:
    """LocationDetailApi 테스트"""

    def test_location_detail_requires_authentication(self, api_client):
        """인증이 필요한 API"""
        location = LocationFactory()
        url = reverse('locations:detail', kwargs={'location_id': location.id})

        response = api_client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_location_detail_success(self, authenticated_api_client):
        """정상적인 장소 상세 조회"""
        location = LocationFactory(name='마루180', max_capacity=180)
        url = reverse('locations:detail', kwargs={'location_id': location.id})

        response = authenticated_api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == location.id
        assert response.data['name'] == '마루180'
        assert response.data['max_capacity'] == 180
        assert response.data['display_capacity'] == '180명'
        assert 'created_at' in response.data
        assert 'updated_at' in response.data

    def test_location_detail_not_found(self, authenticated_api_client):
        """존재하지 않는 장소 조회"""
        url = reverse('locations:detail', kwargs={'location_id': 99999})

        response = authenticated_api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert '장소를 찾을 수 없습니다' in response.data['error']


@pytest.mark.django_db
class TestLocationUpdateApi:
    """LocationUpdateApi 테스트"""

    def test_location_update_requires_admin(self, api_client):
        """어드민 권한 필요"""
        regular_user = UserFactory()
        api_client.force_authenticate(user=regular_user)
        location = LocationFactory()

        url = reverse('locations:update', kwargs={'location_id': location.id})
        data = {'name': '수정된이름'}

        response = api_client.patch(url, data)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_location_update_success(self, api_client):
        """정상적인 장소 정보 수정"""
        admin = AdminUserFactory()
        api_client.force_authenticate(user=admin)
        location = LocationFactory(name='원래이름')

        url = reverse('locations:update', kwargs={'location_id': location.id})
        data = {
            'name': '수정된이름',
            'max_capacity': 200
        }

        response = api_client.patch(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == '수정된이름'
        assert response.data['max_capacity'] == 200

    def test_location_update_not_found(self, api_client):
        """존재하지 않는 장소 수정"""
        admin = AdminUserFactory()
        api_client.force_authenticate(user=admin)

        url = reverse('locations:update', kwargs={'location_id': 99999})
        data = {'name': '수정된이름'}

        response = api_client.patch(url, data)

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestLocationDeleteApi:
    """LocationDeleteApi 테스트"""

    def test_location_delete_requires_admin(self, api_client):
        """어드민 권한 필요"""
        regular_user = UserFactory()
        api_client.force_authenticate(user=regular_user)
        location = LocationFactory()

        url = reverse('locations:delete', kwargs={'location_id': location.id})

        response = api_client.delete(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_location_delete_success(self, api_client):
        """정상적인 장소 삭제"""
        admin = AdminUserFactory()
        api_client.force_authenticate(user=admin)
        location = LocationFactory()
        location_id = location.id

        url = reverse('locations:delete', kwargs={'location_id': location.id})

        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Location.objects.filter(id=location_id).exists()

    def test_location_delete_not_found(self, api_client):
        """존재하지 않는 장소 삭제"""
        admin = AdminUserFactory()
        api_client.force_authenticate(user=admin)

        url = reverse('locations:delete', kwargs={'location_id': 99999})

        response = api_client.delete(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestLocationSuitableApi:
    """LocationSuitableApi 테스트"""

    def test_location_suitable_requires_authentication(self, api_client):
        """인증이 필요한 API"""
        url = reverse('locations:suitable')

        response = api_client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_location_suitable_success(self, authenticated_api_client):
        """적절한 장소 목록 조회 성공"""
        SmallLocationFactory(name='회의실A', max_capacity=20)
        SmallLocationFactory(name='회의실B', max_capacity=50)
        LargeLocationFactory(name='대강당', max_capacity=200)

        url = reverse('locations:suitable')
        response = authenticated_api_client.get(url, {'participant_count': 30})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2  # 50명, 200명 장소만
        capacities = [loc['max_capacity'] for loc in response.data]
        assert 50 in capacities
        assert 200 in capacities

    def test_location_suitable_missing_parameter(self, authenticated_api_client):
        """필수 파라미터 누락"""
        url = reverse('locations:suitable')

        response = authenticated_api_client.get(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_location_suitable_invalid_parameter(self, authenticated_api_client):
        """잘못된 파라미터"""
        url = reverse('locations:suitable')

        response = authenticated_api_client.get(url, {'participant_count': 0})

        assert response.status_code == status.HTTP_400_BAD_REQUEST


# Pytest fixtures
@pytest.fixture
def api_client():
    """API 클라이언트"""
    return APIClient()


@pytest.fixture
def authenticated_api_client(api_client):
    """인증된 API 클라이언트"""
    user = UserFactory()
    api_client.force_authenticate(user=user)
    return api_client