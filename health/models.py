from django.db import models

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class AntreanKesehatan(models.Model):
    """
    Model utama untuk antrean kesehatan.
    Satu record = satu pendaftaran antrean oleh user.
    """

    POLI_CHOICES = [
        ('umum',    'Poli Umum'),
        ('gigi',    'Poli Gigi'),
        ('kia',     'KIA / Kebidanan'),
        ('lansia',  'Poli Lansia'),
        ('gizi',    'Poli Gizi'),
    ]

    STATUS_CHOICES = [
        ('menunggu', 'Menunggu'),
        ('hadir', 'Hadir'),
        ('selesai',  'Selesai'),
        ('expired',  'Expired'),
        ('batal',    'Batal'),
    ]

    # ── Relasi ke User ──────────────────────────────────────────────
    user            = models.ForeignKey(
                        User,
                        on_delete=models.CASCADE,
                        related_name='antrean_kesehatan'
                      )

    # ── Data Pendaftaran ────────────────────────────────────────────
    nama_pasien     = models.CharField(max_length=150)
    nik             = models.CharField(max_length=16)
    no_hp           = models.CharField(max_length=15)
    no_bpjs         = models.CharField(max_length=20, blank=True, null=True)
    keluhan         = models.TextField()

    # ── Jadwal ─────────────────────────────────────────────────────
    poli            = models.CharField(max_length=10, choices=POLI_CHOICES)
    tanggal_kunjungan = models.DateField()

    # ── Antrean ─────────────────────────────────────────────────────
    nomor_antrean   = models.PositiveIntegerField()          # mis: 97
    kode_unik       = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    # ── Estimasi Waktu ──────────────────────────────────────────────
    estimasi_mulai  = models.TimeField()    # mis: 09:00
    estimasi_selesai = models.TimeField()  # mis: 09:15

    # ── Status & Diagnosa (diisi Nakes) ────────────────────────────
    status          = models.CharField(max_length=10, choices=STATUS_CHOICES, default='menunggu')
    diagnosa        = models.CharField(max_length=255, blank=True, null=True)
    resep_obat      = models.TextField(blank=True, null=True)
    catatan_nakes   = models.TextField(blank=True, null=True)

    # ── Nakes yang menangani ────────────────────────────────────────
    ditangani_oleh  = models.ForeignKey(
                        User,
                        on_delete=models.SET_NULL,
                        null=True, blank=True,
                        related_name='antrean_ditangani'
                      )
    waktu_selesai   = models.DateTimeField(null=True, blank=True)

    # ── Timestamps ──────────────────────────────────────────────────
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Antrean Kesehatan'
        verbose_name_plural = 'Antrean Kesehatan'
        ordering            = ['tanggal_kunjungan', 'nomor_antrean']

        # Nomor antrean unik per poli per tanggal
        unique_together = [['poli', 'tanggal_kunjungan', 'nomor_antrean']]

    def __str__(self):
        return (
            f"[{self.tanggal_kunjungan}] {self.get_poli_display()} "
            f"- No.{self.nomor_antrean:03d} - {self.nama_pasien}"
        )

    @property
    def nomor_antrean_display(self):
        """Format nomor antrean 3 digit, contoh: 097"""
        return f"{self.nomor_antrean:03d}"

    @property
    def is_expired(self):
        """
        Antrean dianggap expired jika:
        - tanggal kunjungan sudah lewat HARI INI, DAN
        - status masih 'menunggu'
        """
        today = timezone.localdate()
        if self.status == 'menunggu' and self.tanggal_kunjungan < today:
            return True
        return False

    @property
    def status_display_auto(self):
        """Status yang mempertimbangkan expired otomatis."""
        if self.is_expired:
            return 'expired'
        return self.status

    def get_checkin_url(self, request=None):
        """URL unik untuk QR code verifikasi petugas."""
        path = f"/layanan/kesehatan/checkin/{self.kode_unik}/"
        if request:
            return request.build_absolute_uri(path)
        return path