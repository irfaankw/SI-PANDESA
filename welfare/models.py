# welfare/models.py
from django.db import models
from django.contrib.auth.models import User
import datetime, random, string


class UMKM(models.Model):
    STATUS_CHOICES = [
        ('pending',  'Menunggu Verifikasi'),
        ('aktif',    'Aktif'),
        ('nonaktif', 'Nonaktif'),
    ]

    pemilik         = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='umkm'
    )
    nama_usaha      = models.CharField(max_length=150)
    deskripsi       = models.TextField(blank=True, null=True)
    alamat_usaha    = models.CharField(max_length=255, blank=True, null=True)
    status          = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    nomor_pengajuan = models.CharField(max_length=20, unique=True, blank=True, editable=False)  # ← editable=False

    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'UMKM'
        verbose_name_plural = 'Daftar UMKM'

    def __str__(self):
        return f"{self.nama_usaha} — {self.nama_pemilik}"

    def save(self, *args, **kwargs):
        if not self.nomor_pengajuan:
            tahun = datetime.datetime.now().strftime('%Y%m')
            acak  = ''.join(random.choices(string.digits, k=4))
            self.nomor_pengajuan = f"UMKM-{tahun}-{acak}"
        super().save(*args, **kwargs)

    @property
    def nama_pemilik(self):
        return self.pemilik.get_full_name() or self.pemilik.username

    @property
    def no_hp_dari_profil(self):
        try:
            return self.pemilik.profile.no_hp or '-'
        except Exception:
            return '-'


class Produk(models.Model):
    KATEGORI_CHOICES = [
        ('pertanian',        'Pertanian'),
        ('kerajinan',        'Kerajinan'),
        ('makanan_minuman',  'Makanan & Minuman'),
        ('jasa',             'Jasa'),
        ('perdagangan',      'Perdagangan'),
        ('herbal',           'Herbal'),
        ('peternakan',       'Peternakan'),
    ]

    umkm        = models.ForeignKey(UMKM, on_delete=models.CASCADE, related_name='produk')
    nama        = models.CharField(max_length=200)
    deskripsi   = models.TextField(blank=True, null=True)
    harga       = models.PositiveIntegerField(help_text='Harga dalam rupiah')
    harga_coret = models.PositiveIntegerField(blank=True, null=True, help_text='Harga sebelum diskon (opsional)')
    kategori    = models.CharField(max_length=20, choices=KATEGORI_CHOICES, default='perdagangan')
    foto        = models.ImageField(upload_to='produk/', blank=True, null=True)
    tags        = models.CharField(max_length=200, blank=True, null=True,
                                   help_text='Pisahkan tag dengan koma. Contoh: organik, segar, lokal')
    aktif       = models.BooleanField(default=True)

    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Produk'
        verbose_name_plural = 'Daftar Produk'
        ordering            = ['-created_at']

    def __str__(self):
        return f"{self.nama} — {self.umkm.nama_usaha}"

    @property
    def diskon_persen(self):
        if self.harga_coret and self.harga_coret > self.harga:
            return round((1 - self.harga / self.harga_coret) * 100)
        return None

    @property
    def no_wa_pemilik(self):
        return self.umkm.no_hp_dari_profil

    @property
    def tags_list(self):
        if self.tags:
            return [t.strip() for t in self.tags.split(',') if t.strip()]
        return []