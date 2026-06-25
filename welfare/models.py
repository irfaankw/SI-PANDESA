# welfare/models.py
from django.db import models
from django.contrib.auth.models import User
import datetime, random, string

class ProgramBansos(models.Model):
    KATEGORI_CHOICES = [
        ('pkh',    'PKH (Program Keluarga Harapan)'),
        ('blt',    'BLT Dana Desa'),
        ('bpnt',   'BPNT (Sembako)'),
        ('kip',    'KIP (Kartu Indonesia Pintar)'),
        ('lainnya','Lainnya'),
    ]

    nama             = models.CharField(max_length=150)
    kategori         = models.CharField(max_length=10, choices=KATEGORI_CHOICES, default='lainnya')
    deskripsi        = models.TextField(blank=True, null=True)
    anggaran         = models.BigIntegerField(default=0, help_text='Total anggaran dalam rupiah')
    kuota_penerima   = models.PositiveIntegerField(default=0, help_text='Maks jumlah penerima')
    aktif            = models.BooleanField(default=True)

    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Program Bansos'
        verbose_name_plural = 'Program Bansos'
        ordering            = ['-aktif', 'nama']

    def __str__(self):
        return self.nama

    @property
    def jumlah_penerima(self):
        return self.pengajuan.filter(status='disetujui').count()

    @property
    def total_tersalur(self):
        """Estimasi: anggaran / kuota * jumlah disetujui"""
        if self.kuota_penerima and self.jumlah_penerima:
            per_orang = self.anggaran // self.kuota_penerima
            return per_orang * self.jumlah_penerima
        return 0


class PengajuanBansos(models.Model):
    STATUS_CHOICES = [
        ('pending',   'Menunggu Verifikasi'),
        ('disetujui', 'Disetujui'),
        ('ditolak',   'Ditolak'),
    ]

    user             = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='pengajuan_bansos'
    )
    program          = models.ForeignKey(
        ProgramBansos, on_delete=models.CASCADE, related_name='pengajuan'
    )
    jumlah_anggota   = models.PositiveIntegerField(default=1, help_text='Jumlah anggota keluarga')
    alasan           = models.TextField(blank=True, null=True, help_text='Alasan pengajuan')
    status           = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    catatan_staff    = models.TextField(blank=True, null=True)

    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Pengajuan Bansos'
        verbose_name_plural = 'Pengajuan Bansos'
        ordering            = ['-created_at']
        # Satu user tidak bisa daftar program yang sama dua kali
        unique_together     = ('user', 'program')

    def __str__(self):
        return f"{self.user.username} — {self.program.nama}"

    @property
    def nama_pemohon(self):
        return self.user.get_full_name() or self.user.username

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