from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone
import random

def avatar_upload_path(instance, filename):
    return f"media/profile_photos/user_{instance.user.id}/{filename}"

def ktp_upload_path(instance, filename):
    return f"media/ktp_documents/user_{instance.user.id}/{filename}"

class UserProfile(models.Model):
    STATUS_CHOICES = [
        ('pending',  'Pending'),
        ('verified', 'Verified'),
    ]

    JENIS_KELAMIN_CHOICES = [
        ('L', 'Laki-laki'),
        ('P', 'Perempuan'),
    ]

    user              = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    avatar            = models.ImageField(upload_to=avatar_upload_path, null=True, blank=True)
    foto_ktp          = models.ImageField(upload_to=ktp_upload_path,    null=True, blank=True)

    nik               = models.CharField(max_length=16, unique=True, null=True, blank=True)
    jenis_kelamin     = models.CharField(max_length=1,  choices=JENIS_KELAMIN_CHOICES, null=True, blank=True)
    tanggal_lahir     = models.DateField(null=True, blank=True)
    no_hp             = models.CharField(max_length=15, null=True, blank=True)

    alamat            = models.CharField(max_length=255, null=True, blank=True)
    rt                = models.CharField(max_length=3,   null=True, blank=True)
    rw                = models.CharField(max_length=3,   null=True, blank=True)
    dusun             = models.CharField(max_length=100, null=True, blank=True)

    pekerjaan         = models.CharField(max_length=100, null=True, blank=True)
    agama             = models.CharField(max_length=50,  null=True, blank=True)

    # ── Verifikasi Admin (KTP) — TETAP ────────────────────────
    status_verifikasi = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    catatan_admin     = models.TextField(null=True, blank=True)

    created_at        = models.DateTimeField(auto_now_add=True)
    updated_at        = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Profil Pengguna'
        verbose_name_plural = 'Profil Pengguna'

    def __str__(self):
        return f"Profil – {self.user.get_full_name() or self.user.username}"

    @property
    def is_verified(self):
        return self.status_verifikasi == 'verified'

    @property
    def avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return None

    @property
    def initials(self):
        fn = self.user.first_name
        ln = self.user.last_name
        return f"{fn[:1].upper()}{ln[:1].upper()}" if fn else self.user.username[:2].upper()
    
class EmailOTP(models.Model):
    email      = models.EmailField()
    code       = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used    = models.BooleanField(default=False)
    attempts   = models.PositiveSmallIntegerField(default=0)

    MAX_ATTEMPTS            = 5
    EXPIRY_MINUTES          = 5
    RESEND_COOLDOWN_SECONDS = 60

    class Meta:
        verbose_name        = 'Kode OTP Email'
        verbose_name_plural = 'Kode OTP Email'
        ordering            = ['-created_at']

    def __str__(self):
        return f"{self.email} – {self.code}"

    @classmethod
    def generate(cls, email):
        email = email.strip().lower()
        code  = f"{random.randint(0, 999999):06d}"
        return cls.objects.create(
            email=email,
            code=code,
            expires_at=timezone.now() + timedelta(minutes=cls.EXPIRY_MINUTES),
        )

    @classmethod
    def can_resend(cls, email):
        email = email.strip().lower()
        last  = cls.objects.filter(email=email).order_by('-created_at').first()
        if not last:
            return True, 0
        elapsed   = (timezone.now() - last.created_at).total_seconds()
        remaining = cls.RESEND_COOLDOWN_SECONDS - elapsed
        return remaining <= 0, max(0, int(remaining))

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at