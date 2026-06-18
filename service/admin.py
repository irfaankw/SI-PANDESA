from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html

from .models import (
    MoveLetterRequest, DomicileLetterRequest, DeathLetterRequest, 
    BirthLetterRequest, PovertyLetterRequest, BusinessLetterRequest, IntroLetterRequest,
)

# ─────────────────────────────────────────────────────────────
# Actions bersama
# ─────────────────────────────────────────────────────────────

@admin.action(description="✅ Setujui pengajuan & generate QR Code")
def approve_requests(modeladmin, request, queryset):
    count = 0
    for obj in queryset.filter(status='pending'):
        obj.status        = 'approved'
        obj.approved_at   = timezone.now()
        obj.catatan_admin = None
        obj.save()   # QR otomatis di-generate oleh BaseLetterRequest.save()
        count += 1
    modeladmin.message_user(request, f"{count} pengajuan disetujui dan QR Code berhasil dibuat.")


@admin.action(description="❌ Tolak pengajuan terpilih")
def reject_requests(modeladmin, request, queryset):
    updated = queryset.filter(status='pending').update(
        status='rejected',
        catatan_admin='Pengajuan ditolak oleh staff desa. Silakan periksa kembali kelengkapan berkas Anda.',
    )
    modeladmin.message_user(request, f"{updated} pengajuan ditolak.")


# ─────────────────────────────────────────────────────────────
# MoveLetterRequest Admin
# ─────────────────────────────────────────────────────────────

@admin.register(MoveLetterRequest)
class MoveLetterRequestAdmin(admin.ModelAdmin):
    list_display    = ('reference_number', 'user_fullname', 'status_badge', 'created_at', 'approved_at', 'has_qr')
    list_filter     = ('status', 'created_at')
    search_fields   = ('reference_number', 'user__first_name', 'user__last_name', 'user__username')
    readonly_fields = ('reference_number', 'created_at', 'updated_at', 'approved_at', 'qr_preview')
    actions         = [approve_requests, reject_requests]

    fieldsets = (
        ('Identitas Pengajuan', {
            'fields': ('reference_number', 'user', 'status', 'created_at', 'updated_at', 'approved_at'),
        }),
        ('Data Form', {
            'fields': ('keperluan', 'jumlah_anggota', 'alamat_tujuan'),
        }),
        ('Dokumen Pendukung', {
            'fields': ('file_kk', 'file_ktp', 'file_pengantar'),
        }),
        ('Tindakan Admin', {
            'fields': ('catatan_admin', 'qr_code', 'qr_preview'),
        }),
    )

    @admin.display(description='Pemohon')
    def user_fullname(self, obj):
        return obj.user.get_full_name() or obj.user.username

    @admin.display(description='Status')
    def status_badge(self, obj):
        colors_map = {
            'pending' : ('#f59e0b', 'Menunggu'),
            'approved': ('#10b981', 'Disetujui'),
            'rejected': ('#ef4444', 'Ditolak'),
        }
        color, label = colors_map.get(obj.status, ('#94a3b8', obj.status))
        return format_html(
            '<span style="color:{};font-weight:600;">● {}</span>', color, label
        )

    @admin.display(description='QR', boolean=True)
    def has_qr(self, obj):
        return bool(obj.qr_code)

    @admin.display(description='Preview QR')
    def qr_preview(self, obj):
        if obj.qr_code:
            return format_html(
                '<img src="{}" width="120" height="120" '
                'style="border:1px solid #e2e8f0;border-radius:8px;padding:4px;">',
                obj.qr_code.url,
            )
        return "QR belum dibuat — generate otomatis saat Setujui."


# ─────────────────────────────────────────────────────────────
# DomicileLetterRequest Admin
# ─────────────────────────────────────────────────────────────

@admin.register(DomicileLetterRequest)
class DomicileLetterRequestAdmin(admin.ModelAdmin):
    list_display    = ('reference_number', 'user_fullname', 'status_badge', 'created_at', 'approved_at', 'has_qr')
    list_filter     = ('status', 'created_at')
    search_fields   = ('reference_number', 'user__first_name', 'user__last_name', 'user__username')
    readonly_fields = ('reference_number', 'created_at', 'updated_at', 'approved_at', 'qr_preview')
    actions         = [approve_requests, reject_requests]

    fieldsets = (
        ('Identitas Pengajuan', {
            'fields': ('reference_number', 'user', 'status', 'created_at', 'updated_at', 'approved_at'),
        }),
        ('Data Form', {
            'fields': ('keperluan', 'tujuan_instansi', 'status_tempat_tinggal',
                       'lama_tinggal_tahun', 'lama_tinggal_bulan'),
        }),
        ('Dokumen Pendukung', {
            'fields': ('file_kk', 'file_ktp', 'file_pengantar'),
        }),
        ('Tindakan Admin', {
            'fields': ('catatan_admin', 'qr_code', 'qr_preview'),
        }),
    )

    @admin.display(description='Pemohon')
    def user_fullname(self, obj):
        return obj.user.get_full_name() or obj.user.username

    @admin.display(description='Status')
    def status_badge(self, obj):
        colors_map = {
            'pending' : ('#f59e0b', 'Menunggu'),
            'approved': ('#10b981', 'Disetujui'),
            'rejected': ('#ef4444', 'Ditolak'),
        }
        color, label = colors_map.get(obj.status, ('#94a3b8', obj.status))
        return format_html(
            '<span style="color:{};font-weight:600;">● {}</span>', color, label
        )

    @admin.display(description='QR', boolean=True)
    def has_qr(self, obj):
        return bool(obj.qr_code)

    @admin.display(description='Preview QR')
    def qr_preview(self, obj):
        if obj.qr_code:
            return format_html(
                '<img src="{}" width="120" height="120" '
                'style="border:1px solid #e2e8f0;border-radius:8px;padding:4px;">',
                obj.qr_code.url,
            )
        return "QR belum dibuat — generate otomatis saat Setujui."


# ─────────────────────────────────────────────────────────────
# DeathLetterRequest Admin
# ─────────────────────────────────────────────────────────────

@admin.register(DeathLetterRequest)
class DeathLetterRequestAdmin(admin.ModelAdmin):
    list_display    = ('reference_number', 'nama_almarhum', 'user_fullname', 'status_badge', 'created_at', 'has_qr')
    list_filter     = ('status', 'created_at', 'jenis_kelamin')
    search_fields   = ('reference_number', 'nama_almarhum', 'nik_almarhum', 'user__first_name', 'user__last_name')
    readonly_fields = ('reference_number', 'created_at', 'updated_at', 'approved_at', 'qr_preview')
    actions         = [approve_requests, reject_requests]

    fieldsets = (
        ('Identitas Pengajuan', {
            'fields': ('reference_number', 'user', 'status', 'created_at', 'updated_at', 'approved_at'),
        }),
        ('Data Almarhum / Almarhumah', {
            'fields': ('nama_almarhum', 'nik_almarhum', 'jenis_kelamin', 'tempat_lahir', 'tanggal_lahir', 
                       'tanggal_kematian', 'tempat_kematian', 'penyebab_kematian'),
        }),
        ('Data Pelapor', {
            'fields': ('hubungan_pelapor',),
        }),
        ('Dokumen Pendukung', {
            'fields': ('file_kk', 'file_ktp_almarhum', 'file_surat_dokter'),
        }),
        ('Tindakan Admin', {
            'fields': ('catatan_admin', 'qr_code', 'qr_preview'),
        }),
    )

    @admin.display(description='Pelapor (User)')
    def user_fullname(self, obj):
        return obj.user.get_full_name() or obj.user.username

    @admin.display(description='Status')
    def status_badge(self, obj):
        colors_map = {
            'pending' : ('#f59e0b', 'Menunggu'),
            'approved': ('#10b981', 'Disetujui'),
            'rejected': ('#ef4444', 'Ditolak'),
        }
        color, label = colors_map.get(obj.status, ('#94a3b8', obj.status))
        return format_html(
            '<span style="color:{};font-weight:600;">● {}</span>', color, label
        )

    @admin.display(description='QR', boolean=True)
    def has_qr(self, obj):
        return bool(obj.qr_code)

    @admin.display(description='Preview QR')
    def qr_preview(self, obj):
        if obj.qr_code:
            return format_html(
                '<img src="{}" width="120" height="120" '
                'style="border:1px solid #e2e8f0;border-radius:8px;padding:4px;">',
                obj.qr_code.url,
            )
        return "QR belum dibuat — generate otomatis saat Setujui."


# ─────────────────────────────────────────────────────────────
# BirthLetterRequest Admin
# ─────────────────────────────────────────────────────────────

@admin.register(BirthLetterRequest)
class BirthLetterRequestAdmin(admin.ModelAdmin):
    list_display    = ('reference_number', 'nama_bayi', 'user_fullname', 'status_badge', 'created_at', 'has_qr')
    list_filter     = ('status', 'created_at', 'jenis_kelamin_bayi')
    search_fields   = ('reference_number', 'nama_bayi', 'nama_ayah', 'nama_ibu', 'user__first_name', 'user__last_name')
    readonly_fields = ('reference_number', 'created_at', 'updated_at', 'approved_at', 'qr_preview')
    actions         = [approve_requests, reject_requests]

    fieldsets = (
        ('Identitas Pengajuan', {
            'fields': ('reference_number', 'user', 'status', 'created_at', 'updated_at', 'approved_at'),
        }),
        ('Data Bayi', {
            'fields': ('nama_bayi', 'jenis_kelamin_bayi', 'tempat_lahir_bayi', 'tanggal_lahir_bayi', 'anak_ke'),
        }),
        ('Data Orang Tua', {
            'fields': ('nama_ayah', 'nik_ayah', 'nama_ibu', 'nik_ibu'),
        }),
        ('Dokumen Pendukung', {
            'fields': ('file_kk', 'file_ktp_ayah', 'file_ktp_ibu', 'file_surat_rs'),
        }),
        ('Tindakan Admin', {
            'fields': ('catatan_admin', 'qr_code', 'qr_preview'),
        }),
    )

    @admin.display(description='Pelapor (User)')
    def user_fullname(self, obj):
        return obj.user.get_full_name() or obj.user.username

    @admin.display(description='Status')
    def status_badge(self, obj):
        colors_map = {
            'pending' : ('#f59e0b', 'Menunggu'),
            'approved': ('#10b981', 'Disetujui'),
            'rejected': ('#ef4444', 'Ditolak'),
        }
        color, label = colors_map.get(obj.status, ('#94a3b8', obj.status))
        return format_html(
            '<span style="color:{};font-weight:600;">● {}</span>', color, label
        )

    @admin.display(description='QR', boolean=True)
    def has_qr(self, obj):
        return bool(obj.qr_code)

    @admin.display(description='Preview QR')
    def qr_preview(self, obj):
        if obj.qr_code:
            return format_html(
                '<img src="{}" width="120" height="120" '
                'style="border:1px solid #e2e8f0;border-radius:8px;padding:4px;">',
                obj.qr_code.url,
            )
        return "QR belum dibuat — generate otomatis saat Setujui."


# ─────────────────────────────────────────────────────────────
# PovertyLetterRequest Admin (Surat Tidak Mampu)
# ─────────────────────────────────────────────────────────────

@admin.register(PovertyLetterRequest)
class PovertyLetterRequestAdmin(admin.ModelAdmin):
    list_display    = ('reference_number', 'user_fullname', 'keperluan', 'status_badge', 'created_at', 'approved_at', 'has_qr')
    list_filter     = ('status', 'keperluan', 'created_at')
    search_fields   = ('reference_number', 'tujuan_instansi', 'user__first_name', 'user__last_name', 'user__username')
    readonly_fields = ('reference_number', 'created_at', 'updated_at', 'approved_at', 'qr_preview')
    actions         = [approve_requests, reject_requests]

    fieldsets = (
        ('Identitas Pengajuan', {
            'fields': ('reference_number', 'user', 'status', 'created_at', 'updated_at', 'approved_at'),
        }),
        ('Data Keterangan Ekonomi', {
            'fields': ('keperluan', 'keperluan_lain', 'tujuan_instansi', 'penghasilan', 'jumlah_tanggungan'),
        }),
        ('Dokumen Pendukung', {
            'fields': ('file_kk', 'file_ktp', 'file_pengantar', 'file_pendukung'),
        }),
        ('Tindakan Admin', {
            'fields': ('catatan_admin', 'qr_code', 'qr_preview'),
        }),
    )

    @admin.display(description='Pemohon')
    def user_fullname(self, obj):
        return obj.user.get_full_name() or obj.user.username

    @admin.display(description='Status')
    def status_badge(self, obj):
        colors_map = {
            'pending' : ('#f59e0b', 'Menunggu'),
            'approved': ('#10b981', 'Disetujui'),
            'rejected': ('#ef4444', 'Ditolak'),
        }
        color, label = colors_map.get(obj.status, ('#94a3b8', obj.status))
        return format_html(
            '<span style="color:{};font-weight:600;">● {}</span>', color, label
        )

    @admin.display(description='QR', boolean=True)
    def has_qr(self, obj):
        return bool(obj.qr_code)

    @admin.display(description='Preview QR')
    def qr_preview(self, obj):
        if obj.qr_code:
            return format_html(
                '<img src="{}" width="120" height="120" '
                'style="border:1px solid #e2e8f0;border-radius:8px;padding:4px;">',
                obj.qr_code.url,
            )
        return "QR belum dibuat — generate otomatis saat Setujui."
    
@admin.register(BusinessLetterRequest)
class BusinessLetterRequestAdmin(admin.ModelAdmin):
    list_display    = ('reference_number', 'nama_usaha', 'user_fullname', 'status_badge', 'created_at', 'approved_at', 'has_qr')
    list_filter     = ('status', 'jenis_usaha', 'created_at')
    search_fields   = ('reference_number', 'nama_usaha', 'user__first_name', 'user__last_name', 'user__username')
    readonly_fields = ('reference_number', 'created_at', 'updated_at', 'approved_at', 'qr_preview')
    actions         = [approve_requests, reject_requests]

    fieldsets = (
        ('Identitas Pengajuan', {
            'fields': ('reference_number', 'user', 'status', 'created_at', 'updated_at', 'approved_at'),
        }),
        ('Data Usaha', {
            'fields': ('nama_usaha', 'jenis_usaha', 'jenis_usaha_lain', 'alamat_usaha', 'lama_usaha_tahun', 'omset_perbulan'),
        }),
        ('Keperluan Surat', {
            'fields': ('keperluan', 'keperluan_lain', 'tujuan_instansi'),
        }),
        ('Dokumen Pendukung', {
            'fields': ('file_ktp', 'file_kk', 'file_foto_usaha'),
        }),
        ('Tindakan Admin', {
            'fields': ('catatan_admin', 'qr_code', 'qr_preview'),
        }),
    )

    @admin.display(description='Pemohon')
    def user_fullname(self, obj):
        return obj.user.get_full_name() or obj.user.username

    @admin.display(description='Status')
    def status_badge(self, obj):
        colors_map = {
            'pending' : ('#f59e0b', 'Menunggu'),
            'approved': ('#10b981', 'Disetujui'),
            'rejected': ('#ef4444', 'Ditolak'),
        }
        color, label = colors_map.get(obj.status, ('#94a3b8', obj.status))
        return format_html(
            '<span style="color:{};font-weight:600;">● {}</span>', color, label
        )

    @admin.display(description='QR', boolean=True)
    def has_qr(self, obj):
        return bool(obj.qr_code)

    @admin.display(description='Preview QR')
    def qr_preview(self, obj):
        if obj.qr_code:
            return format_html(
                '<img src="{}" width="120" height="120" '
                'style="border:1px solid #e2e8f0;border-radius:8px;padding:4px;">',
                obj.qr_code.url,
            )
        return "QR belum dibuat — generate otomatis saat Setujui."
    
@admin.register(IntroLetterRequest)
class IntroLetterRequestAdmin(admin.ModelAdmin):
    list_display    = ('reference_number', 'user_fullname', 'keperluan_display', 'tujuan_instansi', 'status_badge', 'created_at', 'approved_at', 'has_qr')
    list_filter     = ('status', 'keperluan', 'created_at')
    search_fields   = ('reference_number', 'tujuan_instansi', 'keperluan_lain', 'user__first_name', 'user__last_name', 'user__username')
    readonly_fields = ('reference_number', 'created_at', 'updated_at', 'approved_at', 'qr_preview')
    actions         = [approve_requests, reject_requests]

    fieldsets = (
        ('Identitas Pengajuan', {
            'fields': ('reference_number', 'user', 'status', 'created_at', 'updated_at', 'approved_at'),
        }),
        ('Data Pengantar', {
            'fields': ('keperluan', 'keperluan_lain', 'tujuan_instansi', 'keterangan_tambahan'),
        }),
        ('Dokumen Pendukung', {
            'fields': ('file_ktp', 'file_kk', 'file_pendukung'),
        }),
        ('Tindakan Admin', {
            'fields': ('catatan_admin', 'qr_code', 'qr_preview'),
        }),
    )

    @admin.display(description='Pemohon')
    def user_fullname(self, obj):
        return obj.user.get_full_name() or obj.user.username

    @admin.display(description='Keperluan')
    def keperluan_display(self, obj):
        return obj.keperluan_display_full

    @admin.display(description='Status')
    def status_badge(self, obj):
        colors_map = {
            'pending' : ('#f59e0b', 'Menunggu'),
            'approved': ('#10b981', 'Disetujui'),
            'rejected': ('#ef4444', 'Ditolak'),
        }
        color, label = colors_map.get(obj.status, ('#94a3b8', obj.status))
        return format_html(
            '<span style="color:{};font-weight:600;">● {}</span>', color, label
        )

    @admin.display(description='QR', boolean=True)
    def has_qr(self, obj):
        return bool(obj.qr_code)

    @admin.display(description='Preview QR')
    def qr_preview(self, obj):
        if obj.qr_code:
            return format_html(
                '<img src="{}" width="120" height="120" '
                'style="border:1px solid #e2e8f0;border-radius:8px;padding:4px;">',
                obj.qr_code.url,
            )
        return "QR belum dibuat — generate otomatis saat Setujui."