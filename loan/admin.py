from django.contrib import admin
from .models import LoanRecord

@admin.register(LoanRecord)
class LoanRecordAdmin(admin.ModelAdmin):
    list_display = ('loan_id', 'student_username', 'book_name', 'loan_date', 'due_date', 'status_display')
    list_filter = ('status', 'due_date')
    search_fields = ('loan_id', 'student_username', 'student_id', 'book_name')
    readonly_fields = ('loan_id', 'student_username', 'student_id', 'book_id', 'book_name', 'loan_date')
    fields = ('due_date', 'status') + readonly_fields

    def status_display(self, obj):
        return obj.get_status_display_with_overdue()
    status_display.short_description = 'Status'