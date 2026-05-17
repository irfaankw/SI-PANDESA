from django.contrib import admin
from .models import AntreanKesehatan

@admin.register(AntreanKesehatan)
class AntreanAdmin(admin.ModelAdmin):
    readonly_fields = ('kode_unik',)
    list_display = ('nomor_antrean', 'nama_pasien', 'poli', 'status')