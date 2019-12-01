from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from simple_history.admin import SimpleHistoryAdmin
from .models import Task


@admin.register(Task)  # admin.site.register(Task, TaskAdmin)
class TaskAdmin(ImportExportModelAdmin):
    # Si no se declara 'list_display' mostrará por defecto su conversión a string
    list_display = ['name', 'state', 'type', 'pid', 'created_at']

    # Para mostrar campos no editables
    readonly_fields = ['created_at']
    # fields = ['author', 'quote'] # fields = [('author', 'quote')]
    fieldsets = [
        ('Task', {
            'fields': [('name', 'type'), ('pid','state'), ('created_at', 'finished_at')]
        }),
]