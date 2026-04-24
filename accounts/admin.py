from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, SignWord, ASLLetter

@admin.register(User)
# 1. Setup Custom User Admin to handle the new 'age' field and "is_active"
class CustomUserAdmin(UserAdmin):
    model = User
    # Add this line to show columns in the main table
    list_display = ['email','username' , 'first_name', 'last_name', 'age', 'role', 'organization_name','is_staff', 'is_active']
    
    # Filter box on the right side
    list_filter = ('is_active', 'is_staff', 'role')
    
    # Layout when you click on a specific user to EDIT them
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'age', 'phone_number', 'organization_name', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': ('email', 'first_name', 'last_name', 'age', 'role', 'organization_name', 'phone_number')}),
    )
# 2. Setup SignWord Admin with filters and search

@admin.register(SignWord)
class SignWordAdmin(admin.ModelAdmin):
    list_display = ('word', 'category', 'needs_ssl_bypass', 'video_url')
    list_filter = ('category', 'needs_ssl_bypass')
    search_fields = ('word',)

# 3. Register ASLLetter at the bottom
admin.site.register(ASLLetter)