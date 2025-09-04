from django.contrib import admin
from .models import Task, EmailLog


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'created_by', 'created_at', 'updated_at']
    list_filter = ['status', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'status', 'created_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'subject', 'success', 'sent_at']
    list_filter = ['success', 'sent_at']
    search_fields = ['recipient', 'subject']
    readonly_fields = ['sent_at']

    fieldsets = (
        (None, {
            'fields': ('recipient', 'subject', 'message', 'success')
        }),
        ('Error Details', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('sent_at',),
            'classes': ('collapse',)
        }),
    )