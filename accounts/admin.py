from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import SignWord

@admin.register(SignWord)
class SignWordAdmin(admin.ModelAdmin):
    # This is the magic list that tells Django which columns to show
    list_display = ('word', 'category', 'needs_ssl_bypass', 'video_url')
    
    # This adds a filter sidebar on the right so you can sort by category!
    list_filter = ('category', 'needs_ssl_bypass')
    
    # This adds a search bar at the top
    search_fields = ('word',)