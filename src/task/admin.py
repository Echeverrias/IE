from django.contrib import admin
from .models import Task

@admin.register(Task)  # admin.site.register(Task, TaskAdmin)
class TaskAdmin(admin.ModelAdmin):
    # Si no se declara 'list_display' mostrará por defecto su conversión a string
    list_display = ['pid', 'name', 'state', 'type', 'started_at', 'finished_at']

    # Para mostrar campos no editables
    readonly_fields = ['created_at', 'updated_at']
    # fields = ['author', 'quote'] # fields = [('author', 'quote')]
    fieldsets = [
        ('Task', {
            'fields': [('name', 'type'), ('pid','state'), ('description'),]
        }),
        ('Dates', {
            'fields': [('started_at', 'finished_at'), ('created_at', 'updated_at')]
        })
]
