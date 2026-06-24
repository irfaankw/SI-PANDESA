from django.contrib import admin
from .models import Tag, GaleriPhoto


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["nama", "slug", "warna"]
    prepopulated_fields = {"slug": ("nama",)}


@admin.register(GaleriPhoto)
class GaleriPhotoAdmin(admin.ModelAdmin):
    list_display = ["judul", "bulan_tahun_display", "ditampilkan", "urutan"]
    list_editable = ["ditampilkan", "urutan"]
    list_filter = ["ditampilkan", "tags"]
    filter_horizontal = ["tags"]
    search_fields = ["judul", "deskripsi"]
    ordering = ["urutan", "-bulan_tahun"]