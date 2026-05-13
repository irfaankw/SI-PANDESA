from django.db import models
from django.utils.text import slugify


class KategoriStaf(models.TextChoices):
    PIMPINAN       = 'Pimpinan',       'Pimpinan'
    SEKRETARIAT    = 'Sekretariat',    'Sekretariat'
    KEUANGAN       = 'Keuangan',       'Keuangan'
    PELAYANAN      = 'Pelayanan',      'Pelayanan'
    KESEJAHTERAAN  = 'Kesejahteraan',  'Kesejahteraan'
    PENDIDIKAN     = 'Pendidikan',     'Pendidikan'


class StafDesa(models.Model):
    # ── Identitas ──────────────────────────────────────────────────────────
    nama           = models.CharField(max_length=120, verbose_name='Nama Lengkap')
    gelar_depan    = models.CharField(max_length=30, blank=True, verbose_name='Gelar Depan')
    gelar_belakang = models.CharField(max_length=30, blank=True, verbose_name='Gelar Belakang')
    jabatan        = models.CharField(max_length=100, verbose_name='Jabatan')
    kategori       = models.CharField(
        max_length=20,
        choices=KategoriStaf.choices,
        default=KategoriStaf.PIMPINAN,
        verbose_name='Kategori / Divisi'
    )
    slug           = models.SlugField(max_length=160, unique=True, blank=True)

    # ── Kontak ─────────────────────────────────────────────────────────────
    telepon        = models.CharField(max_length=20, blank=True, verbose_name='Nomor Telepon')
    email          = models.EmailField(blank=True, verbose_name='Email')
    alamat         = models.CharField(max_length=200, blank=True, verbose_name='Alamat / Dusun')

    # ── Masa Jabatan ───────────────────────────────────────────────────────
    tahun_mulai    = models.PositiveSmallIntegerField(verbose_name='Tahun Mulai')
    masih_aktif    = models.BooleanField(default=True, verbose_name='Masih Aktif?')
    tahun_selesai  = models.PositiveSmallIntegerField(
        null=True, blank=True,
        verbose_name='Tahun Selesai (kosongkan jika masih aktif)'
    )

    # ── Media ──────────────────────────────────────────────────────────────
    foto           = models.ImageField(
        upload_to='profile_photos/',
        null=True, blank=True,
        verbose_name='Foto Profil'
    )

    # ── Bio ────────────────────────────────────────────────────────────────
    bio            = models.TextField(blank=True, verbose_name='Biografi')

    # ── Meta ───────────────────────────────────────────────────────────────
    urutan         = models.PositiveSmallIntegerField(default=0, verbose_name='Urutan Tampil')
    aktif_tampil   = models.BooleanField(default=True, verbose_name='Tampilkan di Website')
    dibuat         = models.DateTimeField(auto_now_add=True)
    diperbarui     = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Staf Desa'
        verbose_name_plural = 'Staf Desa'
        ordering            = ['urutan', 'nama']

    def __str__(self):
        return f"{self.nama_lengkap} — {self.jabatan}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.nama)
            slug = base_slug
            n = 1
            while StafDesa.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{n}"
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def nama_lengkap(self):
        parts = []
        if self.gelar_depan:
            parts.append(self.gelar_depan)
        parts.append(self.nama)
        if self.gelar_belakang:
            parts.append(self.gelar_belakang)
        return ' '.join(parts)

    @property
    def periode(self):
        if self.masih_aktif:
            return f"Menjabat sejak {self.tahun_mulai} – Sekarang"
        return f"{self.tahun_mulai} – {self.tahun_selesai or '?'}"

    @property
    def inisial(self):
        words = self.nama.split()
        return ''.join(w[0].upper() for w in words[:2])

    @property
    def jumlah_penghargaan(self):
        return self.penghargaan_list.count()


# ── Model Penghargaan (relasi 1 staf → banyak penghargaan) ────────────────────
class Penghargaan(models.Model):
    staf  = models.ForeignKey(
        StafDesa,
        on_delete=models.CASCADE,
        related_name='penghargaan_list',
        verbose_name='Staf'
    )
    judul = models.CharField(max_length=200, verbose_name='Judul Penghargaan')
    tahun = models.PositiveSmallIntegerField(verbose_name='Tahun')

    class Meta:
        verbose_name        = 'Penghargaan'
        verbose_name_plural = 'Penghargaan'
        ordering            = ['-tahun']

    def __str__(self):
        return f"{self.judul} ({self.tahun})"


# ── Model UMKM (relasi 1 staf → banyak UMKM) ─────────────────────────────────
class UMKM(models.Model):
    KATEGORI_USAHA = [
        ('Pertanian Organik', 'Pertanian Organik'),
        ('Perdagangan',       'Perdagangan'),
        ('Kerajinan',         'Kerajinan'),
        ('Kuliner',           'Kuliner'),
        ('Jasa',              'Jasa'),
        ('Peternakan',        'Peternakan'),
        ('Perikanan',         'Perikanan'),
        ('Teknologi',         'Teknologi'),
        ('Lainnya',           'Lainnya'),
    ]

    staf           = models.ForeignKey(
        StafDesa,
        on_delete=models.CASCADE,
        related_name='umkm_list',
        verbose_name='Staf'
    )
    nama_usaha     = models.CharField(max_length=150, verbose_name='Nama Usaha')
    kategori_usaha = models.CharField(
        max_length=50,
        choices=KATEGORI_USAHA,
        default='Lainnya',
        verbose_name='Kategori Usaha'
    )
    # Tag produk disimpan sebagai teks dipisah koma
    # Contoh: "Beras organik, Sayuran segar, Pupuk kompos"
    produk         = models.CharField(
        max_length=300,
        blank=True,
        verbose_name='Produk / Layanan',
        help_text='Pisahkan dengan koma. Contoh: Beras organik, Sayuran segar, Pupuk kompos'
    )
    masih_aktif    = models.BooleanField(default=True, verbose_name='Masih Aktif?')

    class Meta:
        verbose_name        = 'UMKM'
        verbose_name_plural = 'UMKM'

    def __str__(self):
        return f"{self.nama_usaha} ({self.staf.nama})"

    @property
    def produk_list(self):
        """Kembalikan list produk dari string yang dipisah koma."""
        if not self.produk:
            return []
        return [p.strip() for p in self.produk.split(',') if p.strip()]