from re import search

from django.db.models import QuerySet,Q
from typing import Optional

from locations.models import Locations

Locations.objects.mro()
def location_list(*,filters:Optional[dict] = None) -> QuerySet[Locations]:
    filters = filters or {}

    qs = Locations.objects.all()

    if 'search' in filters:
        search_term = filters['search']
        qs = qs.filter(
            Q(name__icontains=search_term) | # __icontains는 뭘까?
            Q(address__icontains=search_term) |
            Q(description__icontains=search_term)
        )
    if 'min_capacity' in filters:
        qs = qs.filter(max_capacity__gte=filters['min_capacity']) # __gte는 뭘까?

    return qs.order_by('name')

def location_get(*,locations_id:int) -> Locations:
    return Locations.objects.get(id=locations_id)

def location_get_by_name(*,name:str) -> Locations:
    return Locations.objects.get(name=name)

def location_get_suitable_for_participants(*,particpant_count:int) -> QuerySet[Locations]:
    return Locations.objects.filter(max_capacity__gte=particpant_count).order_by('max_capacity','name')






