from django.contrib import admin
from .models import ComplaintReport

@admin.register(ComplaintReport)
class ComplaintReportAdmin(admin.ModelAdmin):
    list_display  = ('reference_number', 'user', 'judul', 'kategori', 'status', 'created_at')
    list_filter   = ('status', 'kategori')
    search_fields = ('reference_number', 'judul', 'user__username')
    readonly_fields = ('reference_number', 'created_at', 'updated_at')
    list_editable = ('status',)