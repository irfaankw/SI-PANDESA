import uuid
from datetime import timedelta

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


def complaint_upload_path(instance, filename):
    return f"complaint/user_{instance.user_id}/{filename}"


class ComplaintReport(models.Model):
    STATUS_CHOICES = [
        ('pending',  'Menunggu Verifikasi'),
        ('approved', 'Diterima'),
        ('rejected', 'Ditolak'),
    ]

    KATEGORI_CHOICES = [
        ('infrastruktur',    'Infrastruktur'),
        ('lingkungan',       'Lingkungan'),
        ('keamanan',         'Keamanan'),
        ('sosial',           'Sosial'),
        ('pelayanan_publik', 'Pelayanan Publik'),
        ('lainnya',          'Lainnya'),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='complaint_reports',
        verbose_name='Pelapor',
    )

    reference_number = models.CharField(
        max_length=30, unique=True, editable=False,
        verbose_name='Nomor Aduan',
    )

    judul        = models.CharField(max_length=255, verbose_name='Judul Pengaduan')
    kategori     = models.CharField(max_length=20, choices=KATEGORI_CHOICES, verbose_name='Kategori')
    kategori_lain = models.CharField(max_length=255, blank=True, verbose_name='Kategori Lainnya')
    lokasi       = models.CharField(max_length=255, blank=True, verbose_name='Lokasi Kejadian')
    deskripsi    = models.TextField(verbose_name='Deskripsi Lengkap')
    bukti_foto   = models.FileField(upload_to=complaint_upload_path, null=True, blank=True, verbose_name='Bukti Foto/File')

    status        = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', db_index=True)
    catatan_admin = models.TextField(null=True, blank=True, verbose_name='Catatan Admin')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Laporan Pengaduan'
        verbose_name_plural = 'Laporan Pengaduan'
        ordering            = ['-created_at']

    def __str__(self):
        return f"{self.reference_number} – {self.user.get_full_name() or self.user.username}"

    def save(self, *args, **kwargs):
        if not self.reference_number:
            self.reference_number = self._generate_reference_number()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_reference_number():
        year   = timezone.now().year
        suffix = uuid.uuid4().hex[:6].upper()
        return f"ADU-{year}-{suffix}"

    @property
    def is_pending(self):
        return self.status == 'pending'

    @property
    def is_approved(self):
        return self.status == 'approved'

    @property
    def is_rejected(self):
        return self.status == 'rejected'

    @property
    def kategori_display_full(self):
        if self.kategori == 'lainnya' and self.kategori_lain:
            return self.kategori_lain
        return self.get_kategori_display()