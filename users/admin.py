from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'user_type', 'is_active', 'is_staff')
    search_fields = ('username', 'email')
    list_filter = ('user_type', 'is_active', 'is_staff')
    fields = ('username', 'email', 'user_type', 'is_active', 'is_staff', 'password')
    actions = ['make_regular']

    @admin.action(description='선택한 유저를 정회원으로 변경')
    def make_regular(self, request, queryset):
        updated = queryset.update(user_type=User.UserType.REGULAR)
        self.message_user(request, f"{updated}명의 유저가 정회원으로 변경되었습니다.")