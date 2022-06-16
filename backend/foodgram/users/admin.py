from django.contrib import admin
from django.contrib.auth import get_user_model

from users.models import Follow

User = get_user_model()


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'first_name', 'last_name', 'email',)
    list_filter = ('username', 'email',)


class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author',)
    search_fields = ('user',)


admin.site.register(Follow, FollowAdmin)
