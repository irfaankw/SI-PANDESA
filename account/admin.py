from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):

    list_display = (
        'avatar_thumbnail',
        'get_full_name',
        'get_email',
        'nik',
        'no_hp',
        'status_badge',
        'updated_at',
    )
    list_display_links = ('avatar_thumbnail', 'get_full_name')
    list_filter        = ('status_verifikasi', 'jenis_kelamin')
    search_fields      = ('user__first_name', 'user__last_name', 'user__email', 'nik', 'no_hp')
    ordering           = ('-updated_at',)
    list_per_page      = 25

    actions = ['set_verified', 'set_pending']

    @admin.action(description='✅ Tandai sebagai Verified')
    def set_verified(self, request, queryset):
        updated = queryset.update(status_verifikasi='verified')
        self.message_user(request, f'{updated} profil berhasil diverifikasi.')

    @admin.action(description='⏳ Reset ke Pending')
    def set_pending(self, request, queryset):
        updated = queryset.update(status_verifikasi='pending')
        self.message_user(request, f'{updated} profil direset ke Pending.')

    fieldsets = (
        ('Informasi Akun', {
            'fields': ('user',),
        }),
        ('Foto & Dokumen', {
            'fields': ('avatar_preview', 'avatar', 'ktp_preview', 'foto_ktp'),
        }),
        ('Data Kependudukan', {
            'fields': ('nik', 'jenis_kelamin', 'tanggal_lahir', 'no_hp'),
        }),
        ('Alamat', {
            'fields': ('alamat', 'rt', 'rw', 'dusun'),
        }),
        ('Tambahan', {
            'fields': ('pekerjaan', 'agama'),
        }),
        ('Verifikasi', {
            'fields': ('status_verifikasi', 'catatan_admin'),
            'classes': ('wide',),
        }),
    )
    readonly_fields = ('avatar_preview', 'ktp_preview', 'updated_at', 'created_at')

    @admin.display(description='')
    def avatar_thumbnail(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" style="width:36px;height:36px;border-radius:50%;object-fit:cover;">',
                obj.avatar.url,
            )
        return format_html(
            '<div style="width:36px;height:36px;border-radius:50%;background:#059669;'
            'display:flex;align-items:center;justify-content:center;'
            'color:white;font-size:13px;font-weight:700;">{}</div>',
            obj.initials,
        )

    @admin.display(description='Nama Lengkap', ordering='user__first_name')
    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username

    @admin.display(description='Email', ordering='user__email')
    def get_email(self, obj):
        return obj.user.email

    @admin.display(description='Status')
    def status_badge(self, obj):
        colors = {
            'pending':  ('#fee2e2', '#dc2626'),
            'verified': ('#d1fae5', '#059669'),
        }
        bg, fg = colors.get(obj.status_verifikasi, ('#f1f5f9', '#475569'))
        return format_html(
            '<span style="background:{};color:{};padding:3px 10px;border-radius:999px;'
            'font-size:12px;font-weight:600;">{}</span>',
            bg, fg, obj.get_status_verifikasi_display(),
        )

    @admin.display(description='Preview Avatar')
    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" style="width:80px;height:80px;border-radius:50%;object-fit:cover;'
                'border:3px solid #d1fae5;">',
                obj.avatar.url,
            )
        return mark_safe('<span style="color:#94a3b8;">Belum ada foto</span>')

    @admin.display(description='Preview Foto KTP')
    def ktp_preview(self, obj):
        if obj.foto_ktp:
            return format_html(
                '<a href="{}" target="_blank">'
                '<img src="{}" style="max-width:200px;border-radius:8px;border:1px solid #e2e8f0;">'
                '</a>',
                obj.foto_ktp.url, obj.foto_ktp.url,
            )
        return mark_safe('<span style="color:#94a3b8;">Belum ada foto KTP</span>')