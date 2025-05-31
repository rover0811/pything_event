from typing import Dict,TYPE_CHECKING

from django.core.exceptions import ValidationError
from django.db import transaction

from common.services import model_update
from locations.models import Locations

if TYPE_CHECKING:
    from locations.models import Location
else:
    # 런타임에서는 일반 import 사용
    from locations.models import Location


@transaction.atomic
def location_create(*,name:str,address:str,max_capacity:int,description:str)-> Locations:
    if Locations.objects.filter(name=name).exists(): # 이렇게 하는 이유가 뭐지?
        raise ValidationError(f"'{name}' 장소가 이미 존재합니다.")

    location = Locations(name=name,address=address,max_capacity=max_capacity,description=description) # 이렇게 지정해줘야하는 이유가 뭐지

    location.full_clean()
    location.save()

    return location

@transaction.atomic
def location_update(*,location:Locations,data:Dict)-> Locations:

    updatable_fields = ['name', 'address', 'description', 'max_capacity'] # 이런 식으로 지정하는게 보안 상 중요

    updated_location, has_updated = model_update(
        instance=location,
        fields=updatable_fields,
        data=data
    )
    if has_updated:
        # 예: 장소 정보 변경 알림, 로깅 등
        pass
        # _notify_location_updated(updated_location)

    return updated_location



@transaction.atomic
def location_delete(*, location: Location) -> None:
    """장소 삭제"""
    # 이벤트가 연결되어 있는지 확인
    if hasattr(location, 'events') and location.events.exists():
        raise ValidationError("이벤트가 연결된 장소는 삭제할 수 없습니다.")

    location.delete()
