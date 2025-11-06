from django.contrib import admin
from .models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'role', 'approved', 'date_joined')
    list_filter = ('role', 'approved')
    search_fields = ('username', 'other_name', 'phone_number')
    ordering = ('-date_joined',)
    actions = ['approve_users']

    def approve_users(self, request, queryset):
        """Admin action to approve selected users"""
        updated_count = queryset.update(approved=True)
        self.message_user(request, f"{updated_count} users have been approved.")
    approve_users.short_description = "Approve selected users"      

admin.site.register(User, UserAdmin)
