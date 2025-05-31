"""
Location 서비스 테스트
Django Styleguide: 서비스는 비즈니스 로직을 담으므로 철저히 테스트
"""
import pytest
from django.core.exceptions import ValidationError

from locations.services import location_create, location_update, location_delete
from locations.tests.factories import LocationFactory
from locations.models import Location


@pytest.mark.django_db
class TestLocationCreateService:
    """location_create 서비스 테스트"""

    def test_location_create_success(self):
        """정상적인 장소 생성"""
        location = location_create(
            name="마루180",
            address="서울특별시 강남구 테헤란로 123",
            max_capacity=180,
            description="개발자 커뮤니티 공간"
        )

        assert location.id is not None
        assert location.name == "마루180"
        assert location.address == "서울특별시 강남구 테헤란로 123"
        assert location.max_capacity == 180
        assert location.description == "개발자 커뮤니티 공간"
        assert location.created_at is not None

    def test_location_create_with_empty_description(self):
        """설명 없이 장소 생성"""
        location = location_create(
            name="회의실A",
            address="서울특별시 송파구",
            max_capacity=50
        )

        assert location.description == ""

    def test_location_create_duplicate_name_fails(self):
        """중복 이름으로 장소 생성 실패"""
        LocationFactory(name="마루180")

        with pytest.raises(ValidationError, match="'마루180' 장소가 이미 존재합니다"):
            location_create(
                name="마루180",
                address="다른 주소",
                max_capacity=100
            )

    def test_location_create_invalid_capacity_fails(self):
        """잘못된 수용인원으로 생성 실패"""
        with pytest.raises(ValidationError):
            location_create(
                name="테스트장소",
                address="테스트주소",
                max_capacity=0  # 0은 유효하지 않음
            )

    def test_location_create_negative_capacity_fails(self):
        """음수 수용인원으로 생성 실패"""
        with pytest.raises(ValidationError):
            location_create(
                name="테스트장소",
                address="테스트주소",
                max_capacity=-10
            )


@pytest.mark.django_db
class TestLocationUpdateService:
    """location_update 서비스 테스트"""

    def test_location_update_success(self):
        """정상적인 장소 정보 업데이트"""
        location = LocationFactory(
            name="원래이름",
            address="원래주소",
            max_capacity=100
        )

        updated_location = location_update(
            location=location,
            data={
                'name': '수정된이름',
                'address': '수정된주소',
                'max_capacity': 200,
                'description': '수정된설명'
            }
        )

        assert updated_location.name == '수정된이름'
        assert updated_location.address == '수정된주소'
        assert updated_location.max_capacity == 200
        assert updated_location.description == '수정된설명'

    def test_location_update_partial_data(self):
        """일부 필드만 업데이트"""
        location = LocationFactory(
            name="원래이름",
            address="원래주소",
            max_capacity=100
        )

        updated_location = location_update(
            location=location,
            data={'name': '수정된이름'}
        )

        assert updated_location.name == '수정된이름'
        assert updated_location.address == "원래주소"  # 변경되지 않음
        assert updated_location.max_capacity == 100  # 변경되지 않음

    def test_location_update_empty_data(self):
        """빈 데이터로 업데이트시 변경 없음"""
        location = LocationFactory(name="원래이름")
        original_name = location.name

        updated_location = location_update(location=location, data={})

        assert updated_location.name == original_name

    def test_location_update_invalid_capacity_fails(self):
        """잘못된 수용인원으로 업데이트 실패"""
        location = LocationFactory()

        with pytest.raises(ValidationError):
            location_update(
                location=location,
                data={'max_capacity': 0}
            )

    def test_location_update_duplicate_name_fails(self):
        """중복 이름으로 업데이트 실패"""
        existing_location = LocationFactory(name="기존장소")
        location = LocationFactory(name="수정할장소")

        with pytest.raises(Exception):  # IntegrityError
            location_update(
                location=location,
                data={'name': '기존장소'}
            )


@pytest.mark.django_db
class TestLocationDeleteService:
    """location_delete 서비스 테스트"""

    def test_location_delete_success(self):
        """정상적인 장소 삭제"""
        location = LocationFactory()
        location_id = location.id

        location_delete(location=location)

        # 삭제되었는지 확인
        assert not Location.objects.filter(id=location_id).exists()

    def test_location_delete_with_events_fails(self):
        """이벤트가 연결된 장소 삭제 실패 (향후 구현)"""
        # 현재는 이벤트 모델이 없으므로 테스트 스킵
        # 이벤트 모델 구현 후 다음과 같이 테스트:
        # locations = LocationFactory()
        # EventFactory(locations=locations)
        #
        # with pytest.raises(ValidationError, match="이벤트가 연결된 장소는 삭제할 수 없습니다"):
        #     location_delete(locations=locations)
        pass