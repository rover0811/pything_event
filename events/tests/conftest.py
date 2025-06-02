import pytest
from django.db import transaction
from rest_framework.test import APIClient
from users.tests.factories import UserFactory


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """
    모든 테스트에서 데이터베이스 접근을 허용하고
    각 테스트 후 데이터를 정리합니다.
    """
    pass


@pytest.fixture
def test_event():
    """기본 테스트 이벤트"""
    from events.tests.factories import EventFactory
    return EventFactory()


@pytest.fixture
def test_user():
    """기본 테스트 사용자"""
    return UserFactory()


@pytest.fixture
def authenticated_api_client(test_user):
    """인증된 API 클라이언트"""
    client = APIClient()
    client.force_authenticate(user=test_user)
    return client