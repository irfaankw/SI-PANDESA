from django.db import models
from django.contrib.auth.models import User

def avatar_upload_path(instance, filename):
    return f"media/profile_photos/user_{instance.user.id}/{filename}"

def ktp_upload_path(instance, filename):
    return f"media/ktp_documents/user_{instance.user.id}/{filename}"

class UserProfile(models.Model):
    # ── Hanya 2 status: Pending dan Verified ──────────────────
    STATUS_CHOICES = [
        ('pending',  'Pending'),
        ('verified', 'Verified'),
    ]

    JENIS_KELAMIN_CHOICES = [
        ('L', 'Laki-laki'),
        ('P', 'Perempuan'),
    ]

    user              = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    # ── Foto ──────────────────────────────────────────────────
    avatar            = models.ImageField(upload_to=avatar_upload_path, null=True, blank=True)
    foto_ktp          = models.ImageField(upload_to=ktp_upload_path,    null=True, blank=True)

    # ── Data Kependudukan ─────────────────────────────────────
    nik               = models.CharField(max_length=16, unique=True, null=True, blank=True)
    jenis_kelamin     = models.CharField(max_length=1,  choices=JENIS_KELAMIN_CHOICES, null=True, blank=True)
    tanggal_lahir     = models.DateField(null=True, blank=True)
    no_hp             = models.CharField(max_length=15, null=True, blank=True)

    # ── Alamat ────────────────────────────────────────────────
    alamat            = models.CharField(max_length=255, null=True, blank=True)
    rt                = models.CharField(max_length=3,   null=True, blank=True)
    rw                = models.CharField(max_length=3,   null=True, blank=True)
    dusun             = models.CharField(max_length=100, null=True, blank=True)

    # ── Tambahan ──────────────────────────────────────────────
    pekerjaan         = models.CharField(max_length=100, null=True, blank=True)
    agama             = models.CharField(max_length=50,  null=True, blank=True)

    # ── Verifikasi ────────────────────────────────────────────
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