from django.contrib import admin
from events.models import Event, EventRegistration


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_date', 'start_time', 'end_time', 'location', 'status', 'created_by')
    list_filter = ('status', 'event_date', 'location')
    search_fields = ('title', 'description')
    date_hierarchy = 'event_date'
    ordering = ('-event_date', '-start_time')


@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'event', 'company', 'registered_at')
    list_filter = ('event', 'registered_at')
    search_fields = ('name', 'email', 'company')
    date_hierarchy = 'registered_at'
    ordering = ('-registered_at',)
