from cmath import phase
from typing import Dict, Optional, TYPE_CHECKING
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction

if TYPE_CHECKING:
    from users.models import User
else:
    from django.contrib.auth import get_user_model

    User = get_user_model()


@transaction.atomic
def user_create(*, email: str, name: str, password: str, referrer_id: Optional[int] = None, **kwargs) -> User:
    if User.objects.filter(email=email).exists():
        raise ValidationError('이미 존재하는 이메일입니다.')

    user = User(
        email=email,
        username=email,
        name=name,
        phone=kwargs.get('phone', ''),
        company=kwargs.get('company', ''),
        newsletter_subscribed=kwargs.get('newsletter_subscribed', '')
    )

    if referrer_id:
        referrer = User.objects.get(id=referrer_id)
        if referrer.user_type == User.UserType.NON_MEMBER:
            raise ValidationError('비회원은 추천인이 될 수 없습니다.')

        user.referrer = referrer  # 이 분기는 추천인이 있는 상황
        user.user_type = User.UserType.ASSOCIATE  # 있으면 준회원으로 업그레이드

    user.set_password(password)
    user.full_clean()
    user.save()

    if user.newsletter_subscribed:
        # TODO: 미구현
        pass

    return user


@transaction.atomic
def user_update(*, user: User, data: Dict) -> User:
    updatable_fields = ['name', 'phone', 'company', 'newsletter_subscribed']

    has_updated = False
    for filed_name in updatable_fields:
        if filed_name in data:
            setattr(user, filed_name, data[filed_name])
            has_updated = True

    if has_updated:
        user.full_clean()
        user.save()

    return user


@transaction.atomic
def user_approve(*, user: User, approved_by: User) -> User:
    if user.user_type != User.UserType.ASSOCIATE:
        raise ValidationError('준회원만 정회원으로 승인 가능합니다.')

    if approved_by.user_type != User.UserType.ADMIN:
        raise ValidationError('어드민만 사용자를 승인할 수 있습니다.')

    if approved_by == user:
        raise ValidationError("자기 자신을 승인할 수 없습니다.")

    user.user_type = User.UserType.REGULAR
    user.approved_by = approved_by
    user.full_clean()
    user.save()

    return user


def user_set_referer(*, user: User, referrer: User) -> User:
    if user.referrer:
        raise ValidationError('이미 추천인이 설정된 사용자입니다.')

    if referrer.user_type == User.UserType.NON_MEMBER:
        raise ValidationError('비회원은 추천인이 될 수 없습니다.')

    if referrer.user_type == User.UserType.ASSOCIATE:
        raise ValidationError('준회원은 추천인이 될 수 없습니다.')

    user.referrer = referrer
    if user.user_type == User.UserType.NON_MEMBER:
        user.user_type = User.UserType.ASSOCIATE

    user.full_clean()
    user.save()

    return user
