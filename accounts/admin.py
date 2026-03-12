from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, SignWord

# 1. Setup Custom User Admin to handle the new 'age' field
class CustomUserAdmin(UserAdmin):
    model = User
    # Add this line to show columns in the main table
    list_display = ['username', 'email', 'first_name', 'last_name', 'age', 'is_staff']
    
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('age',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('age',)}),
    )
# 2. Setup SignWord Admin with filters and search
class SignWordAdmin(admin.ModelAdmin):
    list_display = ('word', 'category', 'needs_ssl_bypass', 'video_url')
    list_filter = ('category', 'needs_ssl_bypass')
    search_fields = ('word',)

# 3. Register everything at the bottom (cleanest way)
admin.site.register(User, CustomUserAdmin)
admin.site.register(SignWord, SignWordAdmin)