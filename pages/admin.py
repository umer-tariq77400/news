from django.contrib import admin
from .models import ContactSubmission

@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('name', 'email', 'subject', 'message', 'created_at')

    actions = ['mark_as_read', 'mark_as_unread']

    def mark_as_read(self, request, queryset):
        updated_count = queryset.update(is_read=True)
        self.message_user(request, f"{updated_count} submission(s) marked as read.")
    mark_as_read.short_description = "Mark selected submissions as read"

    def mark_as_unread(self, request, queryset):
        updated_count = queryset.update(is_read=False)
        self.message_user(request, f"{updated_count} submission(s) marked as unread.")
    mark_as_unread.short_description = "Mark selected submissions as unread"    

