from django.contrib import admin
from .models import Presentation, PresentationComment

@admin.register(Presentation)
class PresentationAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'presenter', 'event', 'status', 'created_at')
    search_fields = ('title', 'presenter__username')
    list_filter = ('status', 'event')

@admin.register(PresentationComment)
class PresentationCommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'presentation', 'author_name', 'created_at')
    search_fields = ('presentation__title', 'author_name') 