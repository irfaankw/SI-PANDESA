# Views Staff Desa untuk mengelola pengajuan surat digital.

from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.contrib import messages
from django.db.models import Q, Count, Case, When, IntegerField

from core.decorators import staff_desa_required
from .models import (
    MoveLetterRequest, DomicileLetterRequest, DeathLetterRequest,
    BirthLetterRequest, PovertyLetterRequest, BusinessLetterRequest, IntroLetterRequest,
)

# ─────────────────────────────────────────────────────────────
# Metadata 7 jenis surat
# ─────────────────────────────────────────────────────────────

LETTER_META = [
    (MoveLetterRequest,     'Surat Pindah',          'move'),
    (DomicileLetterRequest, 'Surat Domisili',         'domicile'),
    (DeathLetterRequest,    'Surat Kematian',         'death'),
    (BirthLetterRequest,    'Surat Kelahiran',        'birth'),
    (PovertyLetterRequest,  'Surat Tidak Mampu',      'poverty'),
    (BusinessLetterRequest, 'Surat Keterangan Usaha', 'business'),
    (IntroLetterRequest,    'Surat Pengantar',        'intro'),
]

_SLUG_TO_MODEL = {slug: model for model, _, slug in LETTER_META}
_SLUG_TO_LABEL = {slug: label for model, label, slug in LETTER_META}


def _collect_letters(status_filter=None, search_q=None, jenis_filter=None):
    results = []
    for model, label, slug in LETTER_META:
        if jenis_filter and jenis_filter != 'all' and slug != jenis_filter:
            continue
        qs = model.objects.select_related('user', 'user__profile')
        if status_filter and status_filter != 'all':
            qs = qs.filter(status=status_filter)
        if search_q:
            qs = qs.filter(
                Q(user__first_name__icontains=search_q) |
                Q(user__last_name__icontains=search_q)  |
                Q(user__username__icontains=search_q)   |
                Q(reference_number__icontains=search_q)
            )
        objs = list(qs)
        for obj in objs:
            obj.jenis_surat = label
            obj.slug_surat  = slug
        results.extend(objs)
    return sorted(results, key=lambda x: x.created_at, reverse=True)

def _get_stats():
    total = pending = approved = rejected = 0
    for model, _, _ in LETTER_META:
        row = model.objects.aggregate(
            total    = Count('id'),
            pending  = Count(Case(When(status='pending',  then=1), output_field=IntegerField())),
            approved = Count(Case(When(status='approved', then=1), output_field=IntegerField())),
            rejected = Count(Case(When(status='rejected', then=1), output_field=IntegerField())),
        )
        total    += row['total']
        pending  += row['pending']
        approved += row['approved']
        rejected += row['rejected']
    return {'total': total, 'pending': pending, 'approved': approved, 'rejected': rejected}

# ─────────────────────────────────────────────────────────────
# View 1 — Dashboard utama
# ─────────────────────────────────────────────────────────────

@staff_desa_required
def staff_letter_dashboard(request):
    status_filter = request.GET.get('status', 'all')
    search_q      = request.GET.get('q', '').strip()
    jenis_filter  = request.GET.get('jenis', 'all')

    letters = _collect_letters(status_filter, search_q or None, jenis_filter)
    stats   = _get_stats()

    return render(request, 'service/staff_dashboard.html', {
        'letters'      : letters,
        'stats'        : stats,
        'status_filter': status_filter,
        'jenis_filter' : jenis_filter,
        'search_q'     : search_q,
        'letter_meta'  : LETTER_META,
    })

# ─────────────────────────────────────────────────────────────
# View 2 — Detail + approve/reject
# ─────────────────────────────────────────────────────────────

@staff_desa_required
def staff_letter_detail(request, slug, ref):
    model = _SLUG_TO_MODEL.get(slug)
    if model is None:
        raise Http404("Jenis surat tidak dikenali.")

    letter = get_object_or_404(
        model.objects.select_related('user', 'user__profile'),
        reference_number=ref,
    )
    letter.jenis_surat = _SLUG_TO_LABEL[slug]
    letter.slug_surat  = slug

    if request.method == 'POST':
        action        = request.POST.get('action')
        catatan_admin = request.POST.get('catatan_admin', '').strip()

        if action == 'approve':
            letter.status        = 'approved'
            letter.catatan_admin = catatan_admin or None
            letter.save()
            messages.success(request, f"Surat {letter.reference_number} berhasil disetujui.")
            return redirect('service_staff:letter_dashboard')

        elif action == 'reject':
            if not catatan_admin:
                messages.error(request, "Catatan penolakan wajib diisi sebelum menolak.")
            else:
                letter.status        = 'rejected'
                letter.catatan_admin = catatan_admin
                letter.save()
                messages.success(request, f"Surat {letter.reference_number} telah ditolak.")
                return redirect('service_staff:letter_dashboard')

    specific_fields = letter.get_dashboard_fields()
    supporting_docs = letter.get_supporting_documents()

    return render(request, 'service/staff_detail.html', {
        'letter'         : letter,
        'specific_fields': specific_fields,
        'supporting_docs': supporting_docs,
    })