from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['pid', 'name', 'state', 'type', 'started_at', 'finished_at']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = [
        ('Task', {
            'fields': [('name', 'type'), ('pid','state'), ('description'), ('result')]
        }),
        ('Dates', {
            'fields': [('started_at', 'finished_at'), ('created_at', 'updated_at')]
        })
]