import pytest
from django.db import transaction


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """
    모든 테스트에서 데이터베이스 접근을 허용하고
    각 테스트 후 데이터를 정리합니다.
    """
    pass