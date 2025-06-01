import os
import sys
import django
from django.conf import settings
import pytest

# Django 설정 모듈 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Django 초기화
django.setup()

@pytest.fixture
def api_client():
    """API 클라이언트"""
    from rest_framework.test import APIClient
    return APIClient()
