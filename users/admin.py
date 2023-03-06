from django.contrib import admin
from users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    fields = [
        'username', 'is_active', 'is_superuser', 'is_staff', 'is_spectator',
        'first_name', 'last_name', 'email',
        'picture', 'collation',
        'date_joined', 'last_login',
    ]
    list_display = [
        'username', 'is_active', 'is_superuser', 'is_staff', 'is_spectator',
        'email', 'picture',
        'can_action', 'can_view_all',   # properties
        'date_joined', 'last_login', 'collation',
    ]
    list_editable = ['is_active', 'is_superuser', 'is_staff', 'is_spectator']
    list_filter = ['is_active', 'is_superuser', 'is_staff']
    search_fields = ['username', 'first_name', 'last_name', 'email']

