import uuid
from datetime import timedelta

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MaxValueValidator

from .utils.qr_generator import build_qr_code_file

# ─────────────────────────────────────────────────────────────
# Upload path helpers — generik, dipakai semua jenis surat
# ─────────────────────────────────────────────────────────────

def letter_upload_path(instance, filename):
    """service/<LETTER_SLUG>/user_<id>/<filename>"""
    return f"service/{instance.LETTER_SLUG}/user_{instance.user_id}/{filename}"


def letter_qr_upload_path(instance, filename):
    """service/<LETTER_SLUG>/qr/user_<id>/<filename>"""
    return f"service/{instance.LETTER_SLUG}/qr/user_{instance.user_id}/{filename}"

# ─────────────────────────────────────────────────────────────
# Abstract Base — scaffold yang sama untuk SEMUA surat digital
# ─────────────────────────────────────────────────────────────

class BaseLetterRequest(models.Model):
    """
    Setiap subclass WAJIB mendefinisikan:
    - LETTER_SLUG  : slug folder penyimpanan, mis. 'move_letter'
    - field `user` : redeclare FK agar related_name rapi per jenis surat
                     (lihat alasan di bawah — abstract base tidak bisa
                     punya related_name statis kalau dipakai >1 subclass)
    - field spesifik surat (keperluan, dokumen pendukung, dst.)
    - Meta(BaseLetterRequest.Meta) dengan verbose_name masing-masing

    Opsional:
    - MASA_BERLAKU_BULAN : isi angka kalau surat ini punya masa berlaku
                            (default None = tidak pernah expired)
    """

    STATUS_CHOICES = [
        ('pending',  'Menunggu Verifikasi'),
        ('approved', 'Disetujui'),
        ('rejected', 'Ditolak'),
    ]

    LETTER_SLUG = None
    MASA_BERLAKU_BULAN = None

    reference_number = models.CharField(
        max_length=30, unique=True, editable=False,
        verbose_name='Nomor Pengajuan',
    )

    qr_code = models.ImageField(
        upload_to=letter_qr_upload_path, null=True, blank=True,
        verbose_name='QR Code Verifikasi',
    )

    status        = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', db_index=True, verbose_name='Status Pengajuan')
    catatan_admin = models.TextField(null=True, blank=True, verbose_name='Catatan Admin (jika ditolak)')

    created_at     = models.DateTimeField(auto_now_add=True, verbose_name='Tanggal Pengajuan')
    updated_at     = models.DateTimeField(auto_now=True,     verbose_name='Terakhir Diperbarui')
    approved_at    = models.DateTimeField(null=True, blank=True, verbose_name='Tanggal Disetujui')
    berlaku_hingga = models.DateField(null=True, blank=True, verbose_name='Berlaku Hingga')

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.reference_number} – {self.user.get_full_name() or self.user.username}"

    def save(self, *args, **kwargs):
        if not self.reference_number:
            self.reference_number = self._generate_reference_number()

        if self.status == 'approved' and not self.approved_at:
            self.approved_at = timezone.now()
            if self.MASA_BERLAKU_BULAN:
                self.berlaku_hingga = (
                    timezone.now() + timedelta(days=30 * self.MASA_BERLAKU_BULAN)
                ).date()

        super().save(*args, **kwargs)

        if self.status == 'approved' and not self.qr_code:
            self._generate_qr()

    @staticmethod
    def _generate_reference_number():
        year   = timezone.now().year
        suffix = uuid.uuid4().hex[:6].upper()
        return f"PKU-{year}-{suffix}"

    def _generate_qr(self):
        from django.conf import settings

        base_url   = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')
        verify_url = f"{base_url.rstrip('/')}/layanan/verifikasi/{self.reference_number}/"
        filename   = f"qr_{self.reference_number}.png"

        qr_file = build_qr_code_file(verify_url, filename)
        self.qr_code.save(filename, qr_file, save=False)

        # Update kolom qr_code langsung ke DB tanpa trigger save() lagi
        self.__class__.objects.filter(pk=self.pk).update(qr_code=self.qr_code.name)

    # ── Supporting Documents ──────────────────────────────────
    def get_supporting_documents(self):
        FIELD_CONFIG = {
            'file_ktp':          ('KTP-el Pemohon',        'ktp'),
            'file_kk':           ('Kartu Keluarga',         'kk'),
            'file_pengantar':    ('Surat Pengantar RT/RW',  'doc'),
            'file_ktp_almarhum': ('KTP Almarhum/ah',        'ktp'),
            'file_surat_dokter': ('Surat Ket. Dokter/RS',   'doc'),
            'file_ktp_ayah':     ('KTP-el Ayah',            'ktp'),
            'file_ktp_ibu':      ('KTP-el Ibu',             'ktp'),
            'file_surat_rs':     ('Surat Ket. RS/Bidan',    'doc'),
            'file_foto_usaha':   ('Foto Usaha',             'foto'),
            'file_pendukung':    ('Dokumen Pendukung',       'doc'),
        }
        docs = []
        for field_name, (label, icon) in FIELD_CONFIG.items():
            if hasattr(self, field_name):
                file = getattr(self, field_name)
                if file:
                    docs.append({'label': label, 'url': file.url, 'icon': icon})
        return docs

    # ── Properties ────────────────────────────────────────────
    @property
    def is_pending(self):
        return self.status == 'pending'

    @property
    def is_rejected(self):
        return self.status == 'rejected'

    @property
    def is_approved(self):
        return self.status == 'approved'

    @property
    def is_expired(self):
        return bool(self.berlaku_hingga and self.berlaku_hingga < timezone.now().date())

# ─────────────────────────────────────────────────────────────
# Surat Pindah
# ─────────────────────────────────────────────────────────────

class MoveLetterRequest(BaseLetterRequest):
    LETTER_SLUG = 'move_letter'

    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='move_letter_requests',
        verbose_name='Pemohon',
    )

    keperluan      = models.CharField(max_length=255, verbose_name='Alasan Pindah')
    jumlah_anggota = models.PositiveSmallIntegerField(default=0, verbose_name='Jumlah Anggota Keluarga Ikut')
    alamat_tujuan  = models.CharField(max_length=255, verbose_name='Nama Jalan & RT/RW', blank=True)
    kelurahan      = models.CharField(max_length=100, verbose_name='Kelurahan/Desa', blank=True)
    kecamatan      = models.CharField(max_length=100, verbose_name='Kecamatan', blank=True)
    kota_kabupaten = models.CharField(max_length=100, verbose_name='Kota/Kabupaten', blank=True)
    provinsi       = models.CharField(max_length=100, verbose_name='Provinsi', blank=True)

    file_kk        = models.FileField(upload_to=letter_upload_path, verbose_name='Kartu Keluarga')
    file_ktp       = models.FileField(upload_to=letter_upload_path, verbose_name='KTP-el Pemohon')
    file_pengantar = models.FileField(upload_to=letter_upload_path, verbose_name='Surat Pengantar RT/RW')

    class Meta(BaseLetterRequest.Meta):
        verbose_name        = 'Pengajuan Surat Pindah'
        verbose_name_plural = 'Pengajuan Surat Pindah'
    
    def get_dashboard_fields(self):
        return [
            ('Alasan Pindah',         self.keperluan),
            ('Jumlah Anggota Ikut',   self.jumlah_anggota),
            ('Alamat Tujuan',         self.alamat_tujuan or '—'),
            ('Kelurahan/Desa',        self.kelurahan or '—'),
            ('Kecamatan',             self.kecamatan or '—'),
            ('Kota/Kabupaten',        self.kota_kabupaten or '—'),
            ('Provinsi',              self.provinsi or '—'),
        ]

# ─────────────────────────────────────────────────────────────
# Surat Domisili
# ─────────────────────────────────────────────────────────────

class DomicileLetterRequest(BaseLetterRequest):
    LETTER_SLUG = 'domicile_letter'
    MASA_BERLAKU_BULAN = 6
    STATUS_TEMPAT_TINGGAL_CHOICES = [
        ('milik_sendiri', 'Rumah Milik Sendairi'),
        ('sewa_kontrak',  'Sewa/Kontrak'),
        ('menumpang',     'Menumpang/Tinggal dengan Keluarga'),
        ('dinas',         'Rumah Dinas'),
    ]
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='domicile_letter_requests',
        verbose_name='Pemohon',
    )
    keperluan       = models.CharField(max_length=255, verbose_name='Keperluan / Tujuan Surat')
    tujuan_instansi = models.CharField(max_length=255, verbose_name='Ditujukan Kepada (Instansi Tujuan)')
    status_tempat_tinggal = models.CharField(max_length=20, choices=STATUS_TEMPAT_TINGGAL_CHOICES, verbose_name='Status Tempat Tinggal')
    lama_tinggal_tahun = models.PositiveSmallIntegerField(
        default=0,
        validators=[MaxValueValidator(10)],
        verbose_name='Lama Tinggal (Tahun)',
    )
    lama_tinggal_bulan = models.PositiveSmallIntegerField(
        default=0,
        validators=[MaxValueValidator(11)],
        verbose_name='Lama Tinggal (Bulan)',
    )
    file_kk        = models.FileField(upload_to=letter_upload_path, verbose_name='Kartu Keluarga')
    file_ktp       = models.FileField(upload_to=letter_upload_path, verbose_name='KTP-el Pemohon')
    file_pengantar = models.FileField(upload_to=letter_upload_path, verbose_name='Surat Pengantar RT/RW')

    class Meta(BaseLetterRequest.Meta):
        verbose_name        = 'Pengajuan Surat Domisili'
        verbose_name_plural = 'Pengajuan Surat Domisili'

    def get_dashboard_fields(self):
        return [
            ('Keperluan',             self.keperluan),
            ('Ditujukan Kepada',      self.tujuan_instansi),
            ('Status Tempat Tinggal', self.get_status_tempat_tinggal_display()),
            ('Lama Tinggal',          self.lama_tinggal_display),
        ]

    @property
    def lama_tinggal_display(self):
        if self.lama_tinggal_tahun >= 10:
            return "10 tahun atau lebih"
            
        parts = []
        if self.lama_tinggal_tahun:
            parts.append(f"{self.lama_tinggal_tahun} tahun")
        if self.lama_tinggal_bulan:
            parts.append(f"{self.lama_tinggal_bulan} bulan")
        return " ".join(parts) if parts else "kurang dari 1 bulan"
    
# ─────────────────────────────────────────────────────────────
# Surat Kematian
# ─────────────────────────────────────────────────────────────

class DeathLetterRequest(BaseLetterRequest):
    LETTER_SLUG = 'death_letter'

    JENIS_KELAMIN_CHOICES = [
        ('L', 'Laki-laki'),
        ('P', 'Perempuan'),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='death_letter_requests',
        verbose_name='Pemohon (Pelapor)',
    )

    # ── Data almarhum/almarhumah ──────────────────────────────
    nama_almarhum      = models.CharField(max_length=255, verbose_name='Nama Almarhum/Almarhumah')
    nik_almarhum       = models.CharField(max_length=16,  verbose_name='NIK Almarhum/Almarhumah')
    jenis_kelamin      = models.CharField(max_length=1, choices=JENIS_KELAMIN_CHOICES, verbose_name='Jenis Kelamin')
    tempat_lahir       = models.CharField(max_length=100, verbose_name='Tempat Lahir Almarhum')
    tanggal_lahir      = models.DateField(verbose_name='Tanggal Lahir Almarhum')
    tanggal_kematian   = models.DateField(verbose_name='Tanggal Kematian')
    tempat_kematian    = models.CharField(max_length=255, verbose_name='Tempat Kematian')
    penyebab_kematian  = models.CharField(max_length=255, verbose_name='Penyebab Kematian', blank=True)
    hubungan_pelapor   = models.CharField(max_length=100, verbose_name='Hubungan Pelapor dengan Almarhum')

    # ── Dokumen pendukung ─────────────────────────────────────
    file_kk            = models.FileField(upload_to=letter_upload_path, verbose_name='Kartu Keluarga')
    file_ktp_almarhum  = models.FileField(upload_to=letter_upload_path, verbose_name='KTP-el Almarhum/Almarhumah')
    file_surat_dokter  = models.FileField(upload_to=letter_upload_path, verbose_name='Surat Keterangan Dokter/RS', blank=True, null=True)

    class Meta(BaseLetterRequest.Meta):
        verbose_name        = 'Pengajuan Surat Kematian'
        verbose_name_plural = 'Pengajuan Surat Kematian'

    def get_dashboard_fields(self):
        return [
            ('Nama Almarhum/ah',   self.nama_almarhum),
            ('NIK Almarhum/ah',    self.nik_almarhum),
            ('Jenis Kelamin',      self.get_jenis_kelamin_display()),
            ('Tempat Lahir',       self.tempat_lahir),
            ('Tanggal Lahir',      self.tanggal_lahir),
            ('Tanggal Kematian',   self.tanggal_kematian),
            ('Tempat Kematian',    self.tempat_kematian),
            ('Penyebab Kematian',  self.penyebab_kematian or '—'),
            ('Hubungan Pelapor',   self.hubungan_pelapor),
        ]

# ─────────────────────────────────────────────────────────────
# Surat Kelahiran
# ─────────────────────────────────────────────────────────────

class BirthLetterRequest(BaseLetterRequest):
    LETTER_SLUG = 'birth_letter'

    JENIS_KELAMIN_CHOICES = [
        ('L', 'Laki-laki'),
        ('P', 'Perempuan'),
    ]

    ANAK_KE_CHOICES = [(i, f"Anak ke-{i}") for i in range(1, 16)]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='birth_letter_requests',
        verbose_name='Pemohon (Pelapor)',
    )

    # ── Data bayi ─────────────────────────────────────────────
    nama_bayi          = models.CharField(max_length=255, verbose_name='Nama Bayi')
    jenis_kelamin_bayi = models.CharField(max_length=1, choices=JENIS_KELAMIN_CHOICES, verbose_name='Jenis Kelamin Bayi')
    tanggal_lahir_bayi = models.DateField(verbose_name='Tanggal Lahir Bayi')
    tempat_lahir_bayi  = models.CharField(max_length=255, verbose_name='Tempat Lahir Bayi')
    anak_ke            = models.PositiveSmallIntegerField(default=1, verbose_name='Anak Ke-')

    # ── Data orang tua ────────────────────────────────────────
    nama_ayah          = models.CharField(max_length=255, verbose_name='Nama Ayah')
    nik_ayah           = models.CharField(max_length=16,  verbose_name='NIK Ayah')
    nama_ibu           = models.CharField(max_length=255, verbose_name='Nama Ibu')
    nik_ibu            = models.CharField(max_length=16,  verbose_name='NIK Ibu')

    # ── Dokumen pendukung ─────────────────────────────────────
    file_kk            = models.FileField(upload_to=letter_upload_path, verbose_name='Kartu Keluarga')
    file_ktp_ayah      = models.FileField(upload_to=letter_upload_path, verbose_name='KTP-el Ayah')
    file_ktp_ibu       = models.FileField(upload_to=letter_upload_path, verbose_name='KTP-el Ibu')
    file_surat_rs      = models.FileField(upload_to=letter_upload_path, verbose_name='Surat Keterangan Lahir dari RS/Bidan', blank=True, null=True)

    class Meta(BaseLetterRequest.Meta):
        verbose_name        = 'Pengajuan Surat Kelahiran'
        verbose_name_plural = 'Pengajuan Surat Kelahiran'

    def get_dashboard_fields(self):
        return [
            ('Nama Bayi',            self.nama_bayi),
            ('Jenis Kelamin Bayi',   self.get_jenis_kelamin_bayi_display()),
            ('Tanggal Lahir Bayi',   self.tanggal_lahir_bayi),
            ('Tempat Lahir Bayi',    self.tempat_lahir_bayi),
            ('Anak Ke-',             self.anak_ke),
            ('Nama Ayah',            self.nama_ayah),
            ('NIK Ayah',             self.nik_ayah),
            ('Nama Ibu',             self.nama_ibu),
            ('NIK Ibu',              self.nik_ibu),
        ]

# ─────────────────────────────────────────────────────────────
# Surat Tidak Mampu
# ─────────────────────────────────────────────────────────────

class PovertyLetterRequest(BaseLetterRequest):
    LETTER_SLUG = 'poverty_letter'

    KEPERLUAN_CHOICES = [
        ('beasiswa',        'Pengajuan Beasiswa'),
        ('keringanan_biaya','Keringanan Biaya Pendidikan'),
        ('bantuan_sosial',  'Permohonan Bantuan Sosial'),
        ('keringanan_rs',   'Keringanan Biaya Rumah Sakit'),
        ('lainnya',         'Lainnya'),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='poverty_letter_requests',
        verbose_name='Pemohon',
    )

    keperluan        = models.CharField(max_length=50, choices=KEPERLUAN_CHOICES, verbose_name='Keperluan / Tujuan Surat')
    keperluan_lain   = models.CharField(max_length=255, blank=True, verbose_name='Keperluan Lainnya (jika dipilih Lainnya)')
    tujuan_instansi  = models.CharField(max_length=255, verbose_name='Ditujukan Kepada (Instansi Tujuan)')
    penghasilan      = models.PositiveIntegerField(default=0, verbose_name='Penghasilan Per Bulan (Rp)')
    jumlah_tanggungan= models.PositiveSmallIntegerField(default=0, verbose_name='Jumlah Anggota Keluarga yang Ditanggung')

    file_kk          = models.FileField(upload_to=letter_upload_path, verbose_name='Kartu Keluarga')
    file_ktp         = models.FileField(upload_to=letter_upload_path, verbose_name='KTP-el Pemohon')
    file_pengantar   = models.FileField(upload_to=letter_upload_path, verbose_name='Surat Pengantar RT/RW')
    file_pendukung   = models.FileField(upload_to=letter_upload_path, blank=True, null=True, verbose_name='Dokumen Pendukung (Opsional)')

    class Meta(BaseLetterRequest.Meta):
        verbose_name        = 'Pengajuan Surat Tidak Mampu'
        verbose_name_plural = 'Pengajuan Surat Tidak Mampu'

    def get_dashboard_fields(self):
        return [
            ('Keperluan',          self.keperluan_display_full),
            ('Ditujukan Kepada',   self.tujuan_instansi),
            ('Penghasilan/Bulan',  f"Rp {self.penghasilan:,}".replace(',', '.')),
            ('Jumlah Tanggungan',  self.jumlah_tanggungan),
        ]

    @property
    def keperluan_display_full(self):
        """Tampilkan keperluan_lain jika pilihan adalah 'lainnya'."""
        if self.keperluan == 'lainnya' and self.keperluan_lain:
            return self.keperluan_lain
        return self.get_keperluan_display()
    
# ─────────────────────────────────────────────────────────────
# Surat Keterangan Usaha
# ─────────────────────────────────────────────────────────────

class BusinessLetterRequest(BaseLetterRequest):
    LETTER_SLUG = 'business_letter'
    MASA_BERLAKU_BULAN = 12  # Surat usaha berlaku 1 tahun
 
    JENIS_USAHA_CHOICES = [
        ('perdagangan',   'Perdagangan / Toko'),
        ('pertanian',     'Pertanian / Perkebunan'),
        ('perikanan',     'Perikanan / Tambak'),
        ('jasa',          'Jasa / Servis'),
        ('kerajinan',     'Kerajinan / Industri Rumahan'),
        ('kuliner',       'Kuliner / Warung Makan'),
        ('peternakan',    'Peternakan'),
        ('lainnya',       'Lainnya'),
    ]
 
    KEPERLUAN_CHOICES = [
        ('permodalan',    'Pengajuan Modal / Pinjaman Usaha'),
        ('izin_usaha',    'Pengurusan Izin Usaha (SIUP/NIB)'),
        ('bantuan_pemda', 'Permohonan Bantuan Pemerintah'),
        ('kemitraan',     'Kemitraan / Kerja Sama Usaha'),
        ('lainnya',       'Lainnya'),
    ]
 
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='business_letter_requests',
        verbose_name='Pemohon',
    )
 
    # ── Data usaha ────────────────────────────────────────────
    nama_usaha        = models.CharField(max_length=255, verbose_name='Nama Usaha / Toko')
    jenis_usaha       = models.CharField(max_length=20, choices=JENIS_USAHA_CHOICES, verbose_name='Jenis Usaha')
    jenis_usaha_lain  = models.CharField(max_length=255, blank=True, verbose_name='Jenis Usaha Lainnya')
    alamat_usaha      = models.CharField(max_length=255, verbose_name='Alamat / Lokasi Usaha')
    lama_usaha_tahun  = models.PositiveSmallIntegerField(default=0, verbose_name='Lama Usaha Berjalan (Tahun)')
    omset_perbulan    = models.PositiveIntegerField(default=0, verbose_name='Perkiraan Omset Per Bulan (Rp)')
 
    # ── Keperluan surat ───────────────────────────────────────
    keperluan         = models.CharField(max_length=20, choices=KEPERLUAN_CHOICES, verbose_name='Keperluan Surat')
    keperluan_lain    = models.CharField(max_length=255, blank=True, verbose_name='Keperluan Lainnya')
    tujuan_instansi   = models.CharField(max_length=255, verbose_name='Ditujukan Kepada (Instansi Tujuan)')
 
    # ── Dokumen pendukung ─────────────────────────────────────
    file_ktp          = models.FileField(upload_to=letter_upload_path, verbose_name='KTP-el Pemohon')
    file_kk           = models.FileField(upload_to=letter_upload_path, verbose_name='Kartu Keluarga')
    file_foto_usaha   = models.FileField(upload_to=letter_upload_path, blank=True, null=True, verbose_name='Foto Usaha / Tempat Usaha (Opsional)')
 
    class Meta(BaseLetterRequest.Meta):
        verbose_name        = 'Pengajuan Surat Keterangan Usaha'
        verbose_name_plural = 'Pengajuan Surat Keterangan Usaha'

    def get_dashboard_fields(self):
        return [
            ('Nama Usaha',          self.nama_usaha),
            ('Jenis Usaha',         self.jenis_usaha_display_full),
            ('Alamat Usaha',        self.alamat_usaha),
            ('Lama Usaha (Tahun)', self.lama_usaha_tahun),
            ('Omset/Bulan',         f"Rp {self.omset_perbulan:,}".replace(',', '.')),
            ('Keperluan',           self.keperluan_display_full),
            ('Ditujukan Kepada',    self.tujuan_instansi),
        ]
 
    @property
    def jenis_usaha_display_full(self):
        if self.jenis_usaha == 'lainnya' and self.jenis_usaha_lain:
            return self.jenis_usaha_lain
        return self.get_jenis_usaha_display()
 
    @property
    def keperluan_display_full(self):
        if self.keperluan == 'lainnya' and self.keperluan_lain:
            return self.keperluan_lain
        return self.get_keperluan_display()

# ─────────────────────────────────────────────────────────────
# Surat Pengantar
# ─────────────────────────────────────────────────────────────

class IntroLetterRequest(BaseLetterRequest):
    LETTER_SLUG = 'intro_letter'

    KEPERLUAN_CHOICES = [
        ('pembuatan_ktp',   'Pembuatan / Perpanjangan KTP'),
        ('pembuatan_kk',    'Pembuatan / Perubahan Kartu Keluarga'),
        ('akta_kelahiran',  'Pengurusan Akta Kelahiran'),
        ('akta_kematian',   'Pengurusan Akta Kematian'),
        ('nikah',           'Pengurusan Pernikahan'),
        ('skck',            'Pembuatan SKCK'),
        ('beasiswa',        'Pengajuan Beasiswa'),
        ('perizinan',       'Pengurusan Perizinan / Legalitas'),
        ('lainnya',         'Lainnya'),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='intro_letter_requests',
        verbose_name='Pemohon',
    )

    keperluan        = models.CharField(max_length=50, choices=KEPERLUAN_CHOICES, verbose_name='Keperluan / Tujuan Surat')
    keperluan_lain   = models.CharField(max_length=255, blank=True, verbose_name='Keperluan Lainnya (jika dipilih Lainnya)')
    tujuan_instansi  = models.CharField(max_length=255, verbose_name='Ditujukan Kepada (Instansi / Pihak Tujuan)')
    keterangan_tambahan = models.TextField(max_length=500, blank=True, verbose_name='Keterangan Tambahan (Opsional)')

    file_ktp         = models.FileField(upload_to=letter_upload_path, verbose_name='KTP-el Pemohon')
    file_kk          = models.FileField(upload_to=letter_upload_path, verbose_name='Kartu Keluarga')
    file_pendukung   = models.FileField(upload_to=letter_upload_path, blank=True, null=True, verbose_name='Dokumen Pendukung (Opsional)')

    class Meta(BaseLetterRequest.Meta):
        verbose_name        = 'Pengajuan Surat Pengantar'
        verbose_name_plural = 'Pengajuan Surat Pengantar'

    def get_dashboard_fields(self):
        return [
            ('Keperluan',              self.keperluan_display_full),
            ('Ditujukan Kepada',       self.tujuan_instansi),
            ('Keterangan Tambahan',    self.keterangan_tambahan or '—'),
        ]

    @property
    def keperluan_display_full(self):
        """Tampilkan keperluan_lain jika pilihan adalah 'lainnya'."""
        if self.keperluan == 'lainnya' and self.keperluan_lain:
            return self.keperluan_lain
        return self.get_keperluan_display()