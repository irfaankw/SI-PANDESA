from django.contrib import admin
from django.utils.html import format_html, mark_safe
from .models import StafDesa, Penghargaan, UMKM, Tag, GaleriPhoto


# ── Inline: Penghargaan ───────────────────────────────────────────────────────
class PenghargaanInline(admin.TabularInline):
    model       = Penghargaan
    extra       = 1
    fields      = ('judul', 'tahun')
    ordering    = ('-tahun',)
    verbose_name        = 'Penghargaan'
    verbose_name_plural = '🏅 Pencapaian & Penghargaan'


# ── Inline: UMKM ─────────────────────────────────────────────────────────────
class UMKMInline(admin.StackedInline):
    model       = UMKM
    extra       = 0
    fields      = ('nama_usaha', 'kategori_usaha', 'produk', 'masih_aktif')
    verbose_name        = 'UMKM'
    verbose_name_plural = '🏪 UMKM yang Dikelola'


# ── StafDesa Admin ────────────────────────────────────────────────────────────
@admin.register(StafDesa)
class StafDesaAdmin(admin.ModelAdmin):

    inlines = [PenghargaanInline, UMKMInline]

    list_display  = (
        'foto_thumbnail', 'nama_lengkap_display', 'jabatan',
        'kategori', 'telepon', 'periode_display',
        'aktif_tampil', 'urutan',
    )
    list_display_links = ('foto_thumbnail', 'nama_lengkap_display')
    list_filter   = ('kategori', 'aktif_tampil', 'masih_aktif')
    search_fields = ('nama', 'jabatan', 'telepon', 'email')
    list_editable = ('urutan', 'aktif_tampil')
    ordering      = ('urutan', 'nama')

    prepopulated_fields = {'slug': ('nama',)}
    readonly_fields     = ('dibuat', 'diperbarui', 'foto_preview')

    fieldsets = (
        ('👤 Identitas', {
            'fields': (
                ('gelar_depan', 'nama', 'gelar_belakang'),
                'jabatan',
                'kategori',
                'slug',
            )
        }),
        ('📸 Foto Profil', {
            'fields': ('foto', 'foto_preview'),
        }),
        ('📞 Kontak', {
            'fields': (
                ('telepon', 'email'),
                'alamat',
            ),
        }),
        ('📅 Masa Jabatan', {
            'fields': (
                'tahun_mulai',
                ('masih_aktif', 'tahun_selesai'),
            ),
        }),
        ('📝 Biografi', {
            'fields': ('bio',),
            'description': 'Tulis narasi singkat tentang staf ini. Akan tampil di halaman profil.',
        }),
        ('⚙️ Pengaturan Tampilan', {
            'fields': ('aktif_tampil', 'urutan'),
        }),
        ('🕒 Timestamp', {
            'fields': ('dibuat', 'diperbarui'),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Foto')
    def foto_thumbnail(self, obj):
        if obj.foto:
            return format_html(
                '<img src="{}" style="width:40px;height:40px;'
                'object-fit:cover;border-radius:50%;" />',
                obj.foto.url
            )
        return format_html(
            '<div style="width:40px;height:40px;border-radius:50%;'
            'background:#d1fae5;display:flex;align-items:center;'
            'justify-content:center;font-weight:700;color:#065f46;'
            'font-size:13px;">{}</div>',
            obj.inisial
        )

    @admin.display(description='Nama Lengkap')
    def nama_lengkap_display(self, obj):
        return obj.nama_lengkap

    @admin.display(description='Periode')
    def periode_display(self, obj):
        return obj.periode

    @admin.display(description='Preview Foto')
    def foto_preview(self, obj):
        if obj.foto:
            return format_html(
                '<img src="{}" style="max-height:200px;border-radius:12px;" />',
                obj.foto.url
            )
        return "Belum ada foto"


# ── Register standalone ───────────────────────────────────────────────────────
@admin.register(Penghargaan)
class PenghargaanAdmin(admin.ModelAdmin):
    list_display  = ('judul', 'tahun', 'staf')
    list_filter   = ('tahun',)
    search_fields = ('judul', 'staf__nama')
    ordering      = ('-tahun',)


@admin.register(UMKM)
class UMKMAdmin(admin.ModelAdmin):
    list_display  = ('nama_usaha', 'kategori_usaha', 'staf', 'masih_aktif')
    list_filter   = ('kategori_usaha', 'masih_aktif')
    search_fields = ('nama_usaha', 'staf__nama')


# ── Tag Admin ─────────────────────────────────────────────────────────────────
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display  = ['nama', 'slug', 'warna_preview', 'warna']
    prepopulated_fields = {'slug': ('nama',)}
    search_fields = ['nama']

    @admin.display(description='Preview')
    def warna_preview(self, obj):
        COLOR_MAP = {
            'green':  '#16a34a',
            'blue':   '#3b82f6',
            'yellow': '#eab308',
            'red':    '#ef4444',
            'purple': '#a855f7',
            'orange': '#f97316',
        }
        color = COLOR_MAP.get(obj.warna, '#16a34a')
        return format_html(
            '<span style="display:inline-block;width:16px;height:16px;'
            'border-radius:50%;background:{};vertical-align:middle;"></span> {}',
            color, obj.nama
        )


# ── GaleriPhoto Admin ─────────────────────────────────────────────────────────
@admin.register(GaleriPhoto)
class GaleriPhotoAdmin(admin.ModelAdmin):
    list_display  = ['foto_thumbnail', 'judul', 'bulan_tahun_display', 'tag_list', 'ditampilkan', 'urutan']
    list_editable = ['ditampilkan', 'urutan']
    list_filter   = ['ditampilkan', 'tags']
    filter_horizontal = ['tags']
    search_fields = ['judul', 'deskripsi']
    ordering      = ['urutan', '-bulan_tahun']
    readonly_fields = ['foto_preview']

    fieldsets = (
        ('📷 Foto', {
            'fields': ('foto', 'foto_preview'),
        }),
        ('📝 Informasi', {
            'fields': ('judul', 'deskripsi', 'tags', 'bulan_tahun'),
        }),
        ('⚙️ Pengaturan', {
            'fields': ('ditampilkan', 'urutan'),
        }),
    )

    @admin.display(description='Foto')
    def foto_thumbnail(self, obj):
        if obj.foto:
            return format_html(
                '<img src="{}" style="width:60px;height:45px;'
                'object-fit:cover;border-radius:6px;" />',
                obj.foto.url
            )
        return '—'

    @admin.display(description='Preview')
    def foto_preview(self, obj):
        if obj.foto:
            return format_html(
                '<img src="{}" style="max-height:250px;border-radius:12px;" />',
                obj.foto.url
            )
        return 'Belum ada foto'

    @admin.display(description='Tags')
    def tag_list(self, obj):
        tags = obj.tags.all()
        if not tags:
            return '—'
        COLOR_MAP = {
            'green':  '#16a34a', 'blue':   '#3b82f6',
            'yellow': '#eab308', 'red':    '#ef4444',
            'purple': '#a855f7', 'orange': '#f97316',
        }
        badges = []
        for tag in tags:
            color = COLOR_MAP.get(tag.warna, '#16a34a')
            badges.append(
                '<span style="display:inline-block;padding:2px 8px;border-radius:99px;'
                f'background:{color};color:#fff;font-size:11px;font-weight:600;margin:1px;">{tag.nama}</span>'
            )
        return mark_safe(''.join(badges))