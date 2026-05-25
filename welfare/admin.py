# welfare/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import UMKM, Produk


@admin.register(UMKM)
class UMKMAdmin(admin.ModelAdmin):
    list_display   = (
        'nama_usaha', 'get_pemilik', 'get_email',
        'status_badge', 'nomor_pengajuan', 'created_at'
    )
    list_filter    = ('status',)
    search_fields  = ('nama_usaha', 'pemilik__first_name', 'pemilik__email')
    ordering       = ('-created_at',)
    list_per_page  = 25
    actions        = ['set_aktif', 'set_nonaktif']
    readonly_fields = ('nomor_pengajuan',)   # ← readonly di admin juga

    @admin.action(description='✅ Aktifkan UMKM terpilih')
    def set_aktif(self, request, queryset):
        updated = queryset.update(status='aktif')
        self.message_user(request, f'{updated} UMKM berhasil diaktifkan.')

    @admin.action(description='❌ Nonaktifkan UMKM terpilih')
    def set_nonaktif(self, request, queryset):
        updated = queryset.update(status='nonaktif')
        self.message_user(request, f'{updated} UMKM dinonaktifkan.')

    @admin.display(description='Pemilik', ordering='pemilik__first_name')
    def get_pemilik(self, obj):
        return obj.nama_pemilik

    @admin.display(description='Email', ordering='pemilik__email')
    def get_email(self, obj):
        return obj.pemilik.email

    @admin.display(description='Status')
    def status_badge(self, obj):
        colors = {
            'pending':  ('#fef3c7', '#d97706'),
            'aktif':    ('#d1fae5', '#059669'),
            'nonaktif': ('#fee2e2', '#dc2626'),
        }
        bg, fg = colors.get(obj.status, ('#f1f5f9', '#475569'))
        return format_html(
            '<span style="background:{};color:{};padding:3px 10px;'
            'border-radius:999px;font-size:12px;font-weight:600;">{}</span>',
            bg, fg, obj.get_status_display(),
        )


@admin.register(Produk)
class ProdukAdmin(admin.ModelAdmin):
    list_display  = ('nama', 'get_toko', 'kategori', 'harga', 'aktif', 'created_at')
    list_filter   = ('kategori', 'aktif')
    search_fields = ('nama', 'umkm__nama_usaha')
    ordering      = ('-created_at',)
    list_per_page = 25

    @admin.display(description='Toko', ordering='umkm__nama_usaha')
    def get_toko(self, obj):
        return obj.umkm.nama_usaha