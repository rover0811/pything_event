# conftest.py (프로젝트 루트에 위치)
import os
import sys
import django
from django.conf import settings

# Django 설정 모듈 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Django 초기화
django.setup()