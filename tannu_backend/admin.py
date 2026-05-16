from django.contrib import admin
from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['cert_no', 'name', 'phone', 'start_date', 'end_date', 'paid', 'created_at']
    search_fields = ['name', 'phone', 'cert_no']
    list_filter = ['paid', 'start_date', 'created_at']
    readonly_fields = ['cert_no', 'certificate_file', 'created_at']