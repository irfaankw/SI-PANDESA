from django.db import models
from django.contrib.auth.models import User
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

    # ── Akun (opsional) ────────────────────────────────────────────────────
    # Diisi kalau staf ini punya akun User di sistem (untuk link ke welfare.UMKM).
    # Kosongkan untuk staff lapangan/non-IT yang tidak punya akun.
    user           = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='staf_desa',
        verbose_name='Akun Pengguna (opsional)'
    )

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
    def umkm(self):
        """Kembalikan welfare.UMKM milik staf ini, atau None."""
        if self.user:
            try:
                return self.user.umkm
            except Exception:
                return None
        return None


class Tag(models.Model):
    nama = models.CharField(max_length=50, unique=True, verbose_name="Nama Tag")
    slug = models.SlugField(max_length=60, unique=True, blank=True)
    warna = models.CharField(
        max_length=30,
        default="green",
        verbose_name="Warna Badge",
        help_text="Pilihan: green, blue, yellow, red, purple, orange"
    )

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tag"
        ordering = ["nama"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nama)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nama


class GaleriPhoto(models.Model):
    foto = models.ImageField(upload_to="galeri/%Y/%m/", verbose_name="Foto")
    judul = models.CharField(max_length=120, verbose_name="Judul Foto", blank=True)
    deskripsi = models.TextField(verbose_name="Deskripsi Singkat", blank=True)
    tags = models.ManyToManyField(Tag, blank=True, verbose_name="Tags")
    bulan_tahun = models.DateField(
        verbose_name="Bulan & Tahun",
        help_text="Isi tanggal 1, yang ditampilkan hanya bulan & tahunnya"
    )
    urutan = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Urutan Tampil",
        help_text="Angka lebih kecil tampil lebih dulu"
    )
    ditampilkan = models.BooleanField(default=True, verbose_name="Tampilkan?")
    dibuat_pada = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Foto Galeri"
        verbose_name_plural = "Foto Galeri"
        ordering = ["urutan", "-bulan_tahun"]

    def __str__(self):
        return self.judul or f"Foto {self.pk}"

    def bulan_tahun_display(self):
        BULAN_ID = {
            1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr",
            5: "Mei", 6: "Jun", 7: "Jul", 8: "Agu",
            9: "Sep", 10: "Okt", 11: "Nov", 12: "Des",
        }
        return f"{BULAN_ID[self.bulan_tahun.month]} {self.bulan_tahun.year}"