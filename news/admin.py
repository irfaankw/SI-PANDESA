from django.contrib import admin
from .models import Pengumuman

@admin.register(Pengumuman)
class PengumumanAdmin(admin.ModelAdmin):
    # Kolom yang akan muncul di tabel daftar pengumuman
    list_display = ('judul', 'kategori', 'tanggal_dibuat', 'is_penting')
    
    # Fitur filter di samping kanan
    list_filter = ('kategori', 'is_penting')
    
    # Fitur pencarian berdasarkan judul dan isi
    search_fields = ('judul', 'isi')
    
    # Urutan data (terbaru di atas)
    ordering = ('-tanggal_dibuat',)