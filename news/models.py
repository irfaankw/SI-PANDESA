from django.db import models

class Pengumuman(models.Model):
    KATEGORI_CHOICES = [
        ('SEMUA', 'Semua'),
        ('PENGUMUMAN', 'Pengumuman'),
        ('KEGIATAN', 'Kegiatan'),
        ('LAYANAN', 'Layanan'),
        ('PERINGATAN', 'Peringatan'),
    ]

    judul = models.CharField(max_length=200)
    kategori = models.CharField(max_length=20, choices=KATEGORI_CHOICES, default='PENGUMUMAN')
    isi = models.TextField()
    # Otomatis terhubung ke Supabase Storage lewat settings.py
    gambar = models.ImageField(upload_to='pengumuman/', null=True, blank=True)
    is_penting = models.BooleanField(default=False)
    tanggal_dibuat = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.judul

    class Meta:
        verbose_name_plural = "Pengumuman"