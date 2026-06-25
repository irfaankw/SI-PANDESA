# Views untuk WARGA. Pengajuan surat digital, unduh PDF, verifikasi QR, arsip.

from django.contrib.auth.decorators import login_required
from core.decorators import verified_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404

from .models import (
    MoveLetterRequest, DomicileLetterRequest, DeathLetterRequest,
    BirthLetterRequest, PovertyLetterRequest, BusinessLetterRequest, IntroLetterRequest,
)
from .forms import (
    MoveLetterForm, DomicileLetterForm, DeathLetterForm,
    BirthLetterForm, PovertyLetterForm, BusinessLetterForm, IntroLetterForm,
)

# ─────────────────────────────────────────────────────────────
# Helper private
# ─────────────────────────────────────────────────────────────

def _is_profile_complete(profile):
    if not profile:
        return False
    return all([profile.nik, profile.alamat, profile.rt, profile.rw, profile.dusun])

def _get_profile(user):
    try:
        return user.profile
    except Exception:
        return None

# ─────────────────────────────────────────────────────────────
# Index — daftar 7 layanan surat digital
# ─────────────────────────────────────────────────────────────

@verified_required("Layanan Surat Digital")
def digital_mail_index(request):
    return render(request, 'service/digital_mail.html', {'active_tab': 'surat'})

# ─────────────────────────────────────────────────────────────
# Verifikasi QR — publik, tanpa login
# ─────────────────────────────────────────────────────────────

def verify_letter_view(request, ref):
    LETTER_MAP = [
        (MoveLetterRequest,     'Surat Keterangan Pindah'),
        (DomicileLetterRequest, 'Surat Keterangan Domisili'),
        (DeathLetterRequest,    'Surat Keterangan Kematian'),
        (BirthLetterRequest,    'Surat Keterangan Kelahiran'),
        (PovertyLetterRequest,  'Surat Keterangan Tidak Mampu'),
        (BusinessLetterRequest, 'Surat Keterangan Usaha'),
        (IntroLetterRequest,    'Surat Pengantar'),
    ]
    letter = None
    letter_type = None
    for model, label in LETTER_MAP:
        try:
            letter = model.objects.get(reference_number=ref)
            letter_type = label
            break
        except model.DoesNotExist:
            continue

    if letter is None:
        raise Http404("Surat tidak ditemukan.")

    return render(request, 'service/verify_letter.html', {
        'letter': letter,
        'letter_type': letter_type,
    })

# ─────────────────────────────────────────────────────────────
# Surat Pindah
# ─────────────────────────────────────────────────────────────

@verified_required("Layanan Surat Digital")
def move_letter_view(request):
    profile          = _get_profile(request.user)
    profile_complete = _is_profile_complete(profile)
    latest = MoveLetterRequest.objects.filter(user=request.user).order_by('-created_at').first()

    is_pending_view  = bool(latest and latest.status == 'pending')
    is_rejected_view = bool(latest and latest.status == 'rejected')
    is_approved_view = bool(latest and latest.status == 'approved')

    buat_baru = (request.GET.get('baru') == '1' or request.POST.get('baru') == '1')
    if buat_baru and is_approved_view:
        is_approved_view = False
        latest = None

    if request.method == 'POST':
        if not profile_complete:
            return redirect('service:move_letter')
        if is_pending_view:
            return redirect('service:move_letter')

        form = MoveLetterForm(request.POST, request.FILES)
        if form.is_valid():
            cd = form.cleaned_data
            if is_rejected_view and latest:
                for field in ['keperluan', 'jumlah_anggota', 'alamat_tujuan',
                              'kelurahan', 'kecamatan', 'kota_kabupaten',
                              'provinsi', 'file_kk', 'file_ktp', 'file_pengantar']:
                    setattr(latest, field, cd[field])
                latest.status = 'pending'
                latest.catatan_admin = None
                latest.save()
            else:
                MoveLetterRequest.objects.create(user=request.user, **{
                    k: cd[k] for k in ['keperluan', 'jumlah_anggota', 'alamat_tujuan',
                                       'kelurahan', 'kecamatan', 'kota_kabupaten',
                                       'provinsi', 'file_kk', 'file_ktp', 'file_pengantar']
                })
            return redirect('service:move_letter')

        return render(request, 'service/forms/move_letter.html',
                      _letter_ctx(profile, profile_complete, is_pending_view,
                                  is_rejected_view, is_approved_view, latest, form))

    return render(request, 'service/forms/move_letter.html',
                  _letter_ctx(profile, profile_complete, is_pending_view,
                               is_rejected_view, is_approved_view, latest, MoveLetterForm()))

@login_required
def download_move_letter_pdf(request, ref):
    letter = get_object_or_404(MoveLetterRequest, reference_number=ref,
                                user=request.user, status='approved')
    from .utils.pdf_move_letter import generate_move_letter_pdf
    buffer = generate_move_letter_pdf(letter)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="surat-pindah-{letter.reference_number}.pdf"'
    return response

# ─────────────────────────────────────────────────────────────
# Surat Domisili
# ─────────────────────────────────────────────────────────────

@verified_required("Layanan Surat Digital")
def domicile_letter_view(request):
    profile          = _get_profile(request.user)
    profile_complete = _is_profile_complete(profile)
    latest = DomicileLetterRequest.objects.filter(user=request.user).order_by('-created_at').first()

    is_pending_view  = bool(latest and latest.status == 'pending')
    is_rejected_view = bool(latest and latest.status == 'rejected')
    is_approved_view = bool(latest and latest.status == 'approved')

    buat_baru = (request.GET.get('baru') == '1' or request.POST.get('baru') == '1')
    if buat_baru and is_approved_view:
        is_approved_view = False
        latest = None

    if request.method == 'POST':
        if not profile_complete:
            return redirect('service:domicile_letter')
        if is_pending_view:
            return redirect('service:domicile_letter')

        form = DomicileLetterForm(request.POST, request.FILES)
        if form.is_valid():
            cd = form.cleaned_data
            if is_rejected_view and latest:
                for field in ['keperluan', 'tujuan_instansi', 'status_tempat_tinggal',
                              'lama_tinggal_tahun', 'lama_tinggal_bulan',
                              'file_kk', 'file_ktp', 'file_pengantar']:
                    setattr(latest, field, cd[field])
                latest.status = 'pending'
                latest.catatan_admin = None
                latest.save()
            else:
                DomicileLetterRequest.objects.create(user=request.user, **{
                    k: cd[k] for k in ['keperluan', 'tujuan_instansi', 'status_tempat_tinggal',
                                       'lama_tinggal_tahun', 'lama_tinggal_bulan',
                                       'file_kk', 'file_ktp', 'file_pengantar']
                })
            return redirect('service:domicile_letter')

        return render(request, 'service/forms/domicile_letter.html',
                      _letter_ctx(profile, profile_complete, is_pending_view,
                                  is_rejected_view, is_approved_view, latest, form))

    return render(request, 'service/forms/domicile_letter.html',
                  _letter_ctx(profile, profile_complete, is_pending_view,
                               is_rejected_view, is_approved_view, latest, DomicileLetterForm()))


@login_required
def download_domicile_letter_pdf(request, ref):
    letter = get_object_or_404(DomicileLetterRequest, reference_number=ref,
                                user=request.user, status='approved')
    from .utils.pdf_domicile_letter import generate_domicile_letter_pdf
    buffer = generate_domicile_letter_pdf(letter)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="surat-domisili-{letter.reference_number}.pdf"'
    return response

# ─────────────────────────────────────────────────────────────
# Surat Kematian
# ─────────────────────────────────────────────────────────────

@verified_required("Layanan Surat Digital")
def death_letter_view(request):
    profile          = _get_profile(request.user)
    profile_complete = _is_profile_complete(profile)
    latest = DeathLetterRequest.objects.filter(user=request.user).order_by('-created_at').first()

    is_pending_view  = bool(latest and latest.status == 'pending')
    is_rejected_view = bool(latest and latest.status == 'rejected')
    is_approved_view = bool(latest and latest.status == 'approved')

    buat_baru = (request.GET.get('baru') == '1' or request.POST.get('baru') == '1')
    if buat_baru and is_approved_view:
        is_approved_view = False
        latest = None

    if request.method == 'POST':
        if not profile_complete:
            return redirect('service:death_letter')
        if is_pending_view:
            return redirect('service:death_letter')

        form = DeathLetterForm(request.POST, request.FILES)
        if form.is_valid():
            cd = form.cleaned_data
            if is_rejected_view and latest:
                for field in ['nama_almarhum', 'nik_almarhum', 'jenis_kelamin',
                              'tempat_lahir', 'tanggal_lahir', 'tanggal_kematian',
                              'tempat_kematian', 'penyebab_kematian', 'hubungan_pelapor',
                              'file_kk', 'file_ktp_almarhum']:
                    setattr(latest, field, cd[field])
                if cd.get('file_surat_dokter'):
                    latest.file_surat_dokter = cd['file_surat_dokter']
                latest.status = 'pending'
                latest.catatan_admin = None
                latest.save()
            else:
                kwargs = {k: cd[k] for k in ['nama_almarhum', 'nik_almarhum', 'jenis_kelamin',
                                              'tempat_lahir', 'tanggal_lahir', 'tanggal_kematian',
                                              'tempat_kematian', 'penyebab_kematian', 'hubungan_pelapor',
                                              'file_kk', 'file_ktp_almarhum']}
                if cd.get('file_surat_dokter'):
                    kwargs['file_surat_dokter'] = cd['file_surat_dokter']
                DeathLetterRequest.objects.create(user=request.user, **kwargs)
            return redirect('service:death_letter')

        return render(request, 'service/forms/death_letter.html',
                      _letter_ctx(profile, profile_complete, is_pending_view,
                                  is_rejected_view, is_approved_view, latest, form))

    return render(request, 'service/forms/death_letter.html',
                  _letter_ctx(profile, profile_complete, is_pending_view,
                               is_rejected_view, is_approved_view, latest, DeathLetterForm()))

@login_required
def download_death_letter_pdf(request, ref):
    letter = get_object_or_404(DeathLetterRequest, reference_number=ref,
                                user=request.user, status='approved')
    from .utils.pdf_death_letter import generate_death_letter_pdf
    buffer = generate_death_letter_pdf(letter)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="surat-kematian-{letter.reference_number}.pdf"'
    return response

# ─────────────────────────────────────────────────────────────
# Surat Kelahiran
# ─────────────────────────────────────────────────────────────

@verified_required("Layanan Surat Digital")
def birth_letter_view(request):
    profile          = _get_profile(request.user)
    profile_complete = _is_profile_complete(profile)
    latest = BirthLetterRequest.objects.filter(user=request.user).order_by('-created_at').first()

    is_pending_view  = bool(latest and latest.status == 'pending')
    is_rejected_view = bool(latest and latest.status == 'rejected')
    is_approved_view = bool(latest and latest.status == 'approved')

    buat_baru = (request.GET.get('baru') == '1' or request.POST.get('baru') == '1')
    if buat_baru and is_approved_view:
        is_approved_view = False
        latest = None

    if request.method == 'POST':
        if not profile_complete:
            return redirect('service:birth_letter')
        if is_pending_view:
            return redirect('service:birth_letter')

        form = BirthLetterForm(request.POST, request.FILES)
        if form.is_valid():
            cd = form.cleaned_data
            if is_rejected_view and latest:
                for field in ['nama_bayi', 'jenis_kelamin_bayi', 'tanggal_lahir_bayi',
                              'tempat_lahir_bayi', 'anak_ke', 'nama_ayah', 'nik_ayah',
                              'nama_ibu', 'nik_ibu', 'file_kk', 'file_ktp_ayah', 'file_ktp_ibu']:
                    setattr(latest, field, cd[field])
                if cd.get('file_surat_rs'):
                    latest.file_surat_rs = cd['file_surat_rs']
                latest.status = 'pending'
                latest.catatan_admin = None
                latest.save()
            else:
                kwargs = {k: cd[k] for k in ['nama_bayi', 'jenis_kelamin_bayi', 'tanggal_lahir_bayi',
                                              'tempat_lahir_bayi', 'anak_ke', 'nama_ayah', 'nik_ayah',
                                              'nama_ibu', 'nik_ibu', 'file_kk', 'file_ktp_ayah', 'file_ktp_ibu']}
                if cd.get('file_surat_rs'):
                    kwargs['file_surat_rs'] = cd['file_surat_rs']
                BirthLetterRequest.objects.create(user=request.user, **kwargs)
            return redirect('service:birth_letter')

        return render(request, 'service/forms/birth_letter.html',
                      _letter_ctx(profile, profile_complete, is_pending_view,
                                  is_rejected_view, is_approved_view, latest, form))

    return render(request, 'service/forms/birth_letter.html',
                  _letter_ctx(profile, profile_complete, is_pending_view,
                               is_rejected_view, is_approved_view, latest, BirthLetterForm()))

@login_required
def download_birth_letter_pdf(request, ref):
    letter = get_object_or_404(BirthLetterRequest, reference_number=ref,
                                user=request.user, status='approved')
    from .utils.pdf_birth_letter import generate_birth_letter_pdf
    buffer = generate_birth_letter_pdf(letter)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="surat-kelahiran-{letter.reference_number}.pdf"'
    return response

# ─────────────────────────────────────────────────────────────
# Surat Tidak Mampu
# ─────────────────────────────────────────────────────────────

@verified_required("Layanan Surat Digital")
def poverty_letter_view(request):
    profile          = _get_profile(request.user)
    profile_complete = _is_profile_complete(profile)
    latest = PovertyLetterRequest.objects.filter(user=request.user).order_by('-created_at').first()

    is_pending_view  = bool(latest and latest.status == 'pending')
    is_rejected_view = bool(latest and latest.status == 'rejected')
    is_approved_view = bool(latest and latest.status == 'approved')

    buat_baru = (request.GET.get('baru') == '1' or request.POST.get('baru') == '1')
    if buat_baru and is_approved_view:
        is_approved_view = False
        latest = None

    if request.method == 'POST':
        if not profile_complete:
            return redirect('service:poverty_letter')
        if is_pending_view:
            return redirect('service:poverty_letter')

        form = PovertyLetterForm(request.POST, request.FILES)
        if form.is_valid():
            cd = form.cleaned_data
            if is_rejected_view and latest:
                for field in ['keperluan', 'tujuan_instansi', 'penghasilan',
                              'jumlah_tanggungan', 'file_kk', 'file_ktp', 'file_pengantar']:
                    setattr(latest, field, cd[field])
                latest.keperluan_lain = cd.get('keperluan_lain', '')
                if cd.get('file_pendukung'):
                    latest.file_pendukung = cd['file_pendukung']
                latest.status = 'pending'
                latest.catatan_admin = None
                latest.save()
            else:
                kwargs = {k: cd[k] for k in ['keperluan', 'tujuan_instansi', 'penghasilan',
                                              'jumlah_tanggungan', 'file_kk', 'file_ktp', 'file_pengantar']}
                kwargs['keperluan_lain'] = cd.get('keperluan_lain', '')
                if cd.get('file_pendukung'):
                    kwargs['file_pendukung'] = cd['file_pendukung']
                PovertyLetterRequest.objects.create(user=request.user, **kwargs)
            return redirect('service:poverty_letter')

        return render(request, 'service/forms/poverty_letter.html',
                      _letter_ctx(profile, profile_complete, is_pending_view,
                                  is_rejected_view, is_approved_view, latest, form))

    return render(request, 'service/forms/poverty_letter.html',
                  _letter_ctx(profile, profile_complete, is_pending_view,
                               is_rejected_view, is_approved_view, latest, PovertyLetterForm()))

@login_required
def download_poverty_letter_pdf(request, ref):
    letter = get_object_or_404(PovertyLetterRequest, reference_number=ref,
                                user=request.user, status='approved')
    from .utils.pdf_poverty_letter import generate_poverty_letter_pdf
    buffer = generate_poverty_letter_pdf(letter)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="surat-tidak-mampu-{letter.reference_number}.pdf"'
    return response

# ─────────────────────────────────────────────────────────────
# Surat Keterangan Usaha
# ─────────────────────────────────────────────────────────────

@verified_required("Layanan Surat Digital")
def business_letter_view(request):
    profile          = _get_profile(request.user)
    profile_complete = _is_profile_complete(profile)
    latest = BusinessLetterRequest.objects.filter(user=request.user).order_by('-created_at').first()

    is_pending_view  = bool(latest and latest.status == 'pending')
    is_rejected_view = bool(latest and latest.status == 'rejected')
    is_approved_view = bool(latest and latest.status == 'approved')

    buat_baru = (request.GET.get('baru') == '1' or request.POST.get('baru') == '1')
    if buat_baru and is_approved_view:
        is_approved_view = False
        latest = None

    if request.method == 'POST':
        if not profile_complete:
            return redirect('service:business_letter')
        if is_pending_view:
            return redirect('service:business_letter')

        form = BusinessLetterForm(request.POST, request.FILES)
        if form.is_valid():
            cd = form.cleaned_data
            if is_rejected_view and latest:
                for field in ['nama_usaha', 'jenis_usaha', 'alamat_usaha',
                              'lama_usaha_tahun', 'omset_perbulan', 'keperluan',
                              'tujuan_instansi', 'file_ktp', 'file_kk']:
                    setattr(latest, field, cd[field])
                latest.jenis_usaha_lain = cd.get('jenis_usaha_lain', '')
                latest.keperluan_lain   = cd.get('keperluan_lain', '')
                if cd.get('file_foto_usaha'):
                    latest.file_foto_usaha = cd['file_foto_usaha']
                latest.status = 'pending'
                latest.catatan_admin = None
                latest.save()
            else:
                kwargs = {k: cd[k] for k in ['nama_usaha', 'jenis_usaha', 'alamat_usaha',
                                              'lama_usaha_tahun', 'omset_perbulan', 'keperluan',
                                              'tujuan_instansi', 'file_ktp', 'file_kk']}
                kwargs['jenis_usaha_lain'] = cd.get('jenis_usaha_lain', '')
                kwargs['keperluan_lain']   = cd.get('keperluan_lain', '')
                if cd.get('file_foto_usaha'):
                    kwargs['file_foto_usaha'] = cd['file_foto_usaha']
                BusinessLetterRequest.objects.create(user=request.user, **kwargs)
            return redirect('service:business_letter')

        return render(request, 'service/forms/business_letter.html',
                      _letter_ctx(profile, profile_complete, is_pending_view,
                                  is_rejected_view, is_approved_view, latest, form))

    return render(request, 'service/forms/business_letter.html',
                  _letter_ctx(profile, profile_complete, is_pending_view,
                               is_rejected_view, is_approved_view, latest, BusinessLetterForm()))

@login_required
def download_business_letter_pdf(request, ref):
    letter = get_object_or_404(BusinessLetterRequest, reference_number=ref,
                                user=request.user, status='approved')
    from .utils.pdf_business_letter import generate_business_letter_pdf
    buffer = generate_business_letter_pdf(letter)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="surat-keterangan-usaha-{letter.reference_number}.pdf"'
    return response

# ─────────────────────────────────────────────────────────────
# Surat Pengantar
# ─────────────────────────────────────────────────────────────

@verified_required("Layanan Surat Digital")
def intro_letter_view(request):
    profile          = _get_profile(request.user)
    profile_complete = _is_profile_complete(profile)
    latest = IntroLetterRequest.objects.filter(user=request.user).order_by('-created_at').first()

    is_pending_view  = bool(latest and latest.status == 'pending')
    is_rejected_view = bool(latest and latest.status == 'rejected')
    is_approved_view = bool(latest and latest.status == 'approved')

    buat_baru = (request.GET.get('baru') == '1' or request.POST.get('baru') == '1')
    if buat_baru and is_approved_view:
        is_approved_view = False
        latest = None

    if request.method == 'POST':
        if not profile_complete:
            return redirect('service:intro_letter')
        if is_pending_view:
            return redirect('service:intro_letter')

        form = IntroLetterForm(request.POST, request.FILES)
        if form.is_valid():
            cd = form.cleaned_data
            if is_rejected_view and latest:
                for field in ['keperluan', 'tujuan_instansi', 'file_ktp', 'file_kk']:
                    setattr(latest, field, cd[field])
                latest.keperluan_lain      = cd.get('keperluan_lain', '')
                latest.keterangan_tambahan = cd.get('keterangan_tambahan', '')
                if cd.get('file_pendukung'):
                    latest.file_pendukung = cd['file_pendukung']
                latest.status = 'pending'
                latest.catatan_admin = None
                latest.save()
            else:
                kwargs = {k: cd[k] for k in ['keperluan', 'tujuan_instansi', 'file_ktp', 'file_kk']}
                kwargs['keperluan_lain']      = cd.get('keperluan_lain', '')
                kwargs['keterangan_tambahan'] = cd.get('keterangan_tambahan', '')
                if cd.get('file_pendukung'):
                    kwargs['file_pendukung'] = cd['file_pendukung']
                IntroLetterRequest.objects.create(user=request.user, **kwargs)
            return redirect('service:intro_letter')

        return render(request, 'service/forms/intro_letter.html',
                      _letter_ctx(profile, profile_complete, is_pending_view,
                                  is_rejected_view, is_approved_view, latest, form))

    return render(request, 'service/forms/intro_letter.html',
                  _letter_ctx(profile, profile_complete, is_pending_view,
                               is_rejected_view, is_approved_view, latest, IntroLetterForm()))

@login_required
def download_intro_letter_pdf(request, ref):
    letter = get_object_or_404(IntroLetterRequest, reference_number=ref,
                                user=request.user, status='approved')
    from .utils.pdf_intro_letter import generate_intro_letter_pdf
    buffer = generate_intro_letter_pdf(letter)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="surat-pengantar-{letter.reference_number}.pdf"'
    return response

# ─────────────────────────────────────────────────────────────
# Arsip Surat Warga
# ─────────────────────────────────────────────────────────────

@login_required
def letter_archive_view(request):
    user = request.user
    base_fields = ('reference_number', 'status', 'catatan_admin', 'created_at')

    LETTER_MODELS = [
        (MoveLetterRequest,     'Surat Keterangan Pindah',    'move'),
        (DomicileLetterRequest, 'Surat Keterangan Domisili',  'domicile'),
        (DeathLetterRequest,    'Surat Keterangan Kematian',  'death'),
        (BirthLetterRequest,    'Surat Keterangan Kelahiran', 'birth'),
        (PovertyLetterRequest,  'Surat Keterangan Tidak Mampu','poverty'),
        (BusinessLetterRequest, 'Surat Keterangan Usaha',     'business'),
        (IntroLetterRequest,    'Surat Pengantar',            'intro'),
    ]

    results = []
    for model, jenis, slug in LETTER_MODELS:
        objs = list(model.objects.filter(user=user).only(*base_fields))
        for obj in objs:
            obj.jenis_surat = jenis
            obj.slug_surat  = slug
        results.extend(objs)

    all_letters = sorted(results, key=lambda x: x.created_at, reverse=True)

    profile            = _get_profile(user)
    is_verified        = profile.is_verified if profile else False
    profile_incomplete = bool(profile and not all([profile.nik, profile.alamat, profile.rt]))

    return render(request, 'service/letter_archive.html', {
        'letters'           : all_letters,
        'total'             : len(all_letters),
        'active_tab'        : 'surat',
        'profile'           : profile,
        'is_verified'       : is_verified,
        'profile_incomplete': profile_incomplete,
    })

# ─────────────────────────────────────────────────────────────
# Helper context — satu fungsi untuk semua 7 jenis surat
# ─────────────────────────────────────────────────────────────

def _letter_ctx(profile, profile_complete, is_pending, is_rejected, is_approved, latest, form):
    return {
        'active_tab'       : 'surat',
        'profile'          : profile,
        'profile_complete' : profile_complete,
        'is_pending_view'  : is_pending,
        'is_rejected_view' : is_rejected,
        'is_approved_view' : is_approved,
        'latest_request'   : latest,
        'form'             : form,
    }