from django.contrib.auth import get_user_model
from django.db.models import QuerySet,Q,Count
from typing import Optional,TYPE_CHECKING

if TYPE_CHECKING:
    from users.models import User
else:
    from django.contrib.auth import get_user_model
    User = get_user_model()

def user_list(*,filters:Optional[dict]=None) -> QuerySet[User]:

    filters = filters or {}

    qs = User.objects.select_related('referrer','approved_by')

    if 'user_type' in filters:
        qs = qs.filter(user_type=filters['user_type'])

    if 'newsletter_subscribed' in filters:
        qs = qs.filter(newsletter_subscribed=filters['newsletter_subscribed'])

    if 'search' in filters:
        search_term = filters['search']
        qs = qs.filter(
            Q(username__icontains=search_term) |
            Q(email__icontains=search_term) |
            Q(company__icontains=search_term)
        )
    if 'has_referrer' in filters:
        if filters['has_referrer']:
            qs = qs.filter(referrer__isnull=False)
        else:
            qs = qs.filter(referrer__isnull=True)

    return qs.order_by('-date_joined')

def user_get(*,user_id:int) -> User:
    return User.objects.select_related('referrer','approved_by').get(id=user_id)

def user_get_by_email(*, email: str) -> User:
    return User.objects.get(email=email)

def user_get_pending_approval() -> QuerySet[User]:
    """
    승인 대기 중인 준회원 목록
    """
    return User.objects.filter(
        user_type=User.UserType.ASSOCIATE,
        approved_by__isnull=True
    ).select_related('referrer').order_by('date_joined')

