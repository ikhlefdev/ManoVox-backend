from django.contrib import admin
from .models import Event

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'date', 'location', 'created_at')
    list_filter = ('date', 'location')
    search_fields = ('title', 'description', 'location')
