from .models import (
    MoveLetterRequest, DomicileLetterRequest, DeathLetterRequest,
    BirthLetterRequest, PovertyLetterRequest, BusinessLetterRequest, IntroLetterRequest,
)

LETTER_MODELS = [
    MoveLetterRequest, DomicileLetterRequest, DeathLetterRequest,
    BirthLetterRequest, PovertyLetterRequest, BusinessLetterRequest, IntroLetterRequest,
]

def ringkasan_sidebar(request):
    if not request.user.is_authenticated or request.user.is_staff or request.user.is_superuser:
        return {}

    from health.models import AntreanKesehatan
    from complaint.models import ComplaintReport

    surat_disetujui = sum(
        m.objects.filter(user=request.user, status='approved').count()
        for m in LETTER_MODELS
    )

    return {
        'surat_disetujui':  surat_disetujui,
        'total_kunjungan':  AntreanKesehatan.objects.filter(user=request.user, status='selesai').count(),
        'total_pengaduan':  ComplaintReport.objects.filter(user=request.user).count(),
    }