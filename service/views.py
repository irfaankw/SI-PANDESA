from django.contrib.auth.decorators import login_required
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
# Helper
# ─────────────────────────────────────────────────────────────

def _is_profile_complete(profile):
    if not profile:
        return False
    return all([
        profile.nik,
        profile.alamat,
        profile.rt,
        profile.rw,
        profile.dusun,
    ])


def _get_profile(user):
    try:
        return user.profile
    except Exception:
        return None


# ─────────────────────────────────────────────────────────────
# Index — daftar 7 layanan surat digital
# ─────────────────────────────────────────────────────────────

@login_required
def digital_mail_index(request):
    return render(request, 'service/digital_mail.html', {
        'active_tab': 'surat',
    })

# ─────────────────────────────────────────────────────────────
# Verifikasi QR — publik, tanpa login
# ─────────────────────────────────────────────────────────────

def verify_letter_view(request, ref):
    letter = None
    letter_type = None

    # 1. Cek di Surat Pindah
    try:
        letter = MoveLetterRequest.objects.get(reference_number=ref)
        letter_type = 'Surat Keterangan Pindah'
    except MoveLetterRequest.DoesNotExist:
        pass

    # 2. Cek di Surat Domisili
    if letter is None:
        try:
            letter = DomicileLetterRequest.objects.get(reference_number=ref)
            letter_type = 'Surat Keterangan Domisili'
        except DomicileLetterRequest.DoesNotExist:
            pass

    # 3. Cek di Surat Kematian
    if letter is None:
        try:
            letter = DeathLetterRequest.objects.get(reference_number=ref)
            letter_type = 'Surat Keterangan Kematian'
        except DeathLetterRequest.DoesNotExist:
            pass

    # 4. Cek di Surat Kelahiran
    if letter is None:
        try:
            letter = BirthLetterRequest.objects.get(reference_number=ref)
            letter_type = 'Surat Keterangan Kelahiran'
        except BirthLetterRequest.DoesNotExist:
            pass

    # 4. Cek di Surat Tidak Mampu
    if letter is None:
       try:
           letter = PovertyLetterRequest.objects.get(reference_number=ref)
           letter_type = 'Surat Keterangan Tidak Mampu'
       except PovertyLetterRequest.DoesNotExist:
           pass

    # 4. Cek di Surat Keterangan Usaha
    if letter is None:
       try:
           letter = BusinessLetterRequest.objects.get(reference_number=ref)
           letter_type = 'Surat Keterangan Usaha'
       except BusinessLetterRequest.DoesNotExist:
           pass

    # Cek di Surat Pengantar
    if letter is None:
       try:
           letter = IntroLetterRequest.objects.get(reference_number=ref)
           letter_type = 'Surat Pengantar'
       except IntroLetterRequest.DoesNotExist:
           pass

    # Jika semua model dicari dan tetap tidak ada
    if letter is None:
        raise Http404("Surat tidak ditemukan.")

    return render(request, 'service/verify_letter.html', {
        'letter': letter,
        'letter_type': letter_type,
    })

# ─────────────────────────────────────────────────────────────
# Surat Pindah
# ─────────────────────────────────────────────────────────────

@login_required
def move_letter_view(request):
    profile          = _get_profile(request.user)
    profile_complete = _is_profile_complete(profile)

    latest = MoveLetterRequest.objects.filter(
        user=request.user
    ).order_by('-created_at').first()

    is_pending_view  = bool(latest and latest.status == 'pending')
    is_rejected_view = bool(latest and latest.status == 'rejected')
    is_approved_view = bool(latest and latest.status == 'approved')

    buat_baru = (request.GET.get('baru') == '1' or request.POST.get('baru') == '1')
    if buat_baru and is_approved_view:
        is_approved_view = False
        latest = None  # Paksa latest jadi None agar sistem tahu ini murni buat baru, bukan edit data approved!

    # ── POST ──────────────────────────────────────────────────
    if request.method == 'POST':
        if not profile_complete:
            return redirect('service:move_letter')
        if is_pending_view:
            return redirect('service:move_letter')

        form = MoveLetterForm(request.POST, request.FILES)

        if form.is_valid():
            cd = form.cleaned_data
            if is_rejected_view and latest:
                latest.keperluan      = cd['keperluan']
                latest.jumlah_anggota = cd['jumlah_anggota']
                latest.alamat_tujuan  = cd['alamat_tujuan']
                latest.kelurahan      = cd['kelurahan']
                latest.kecamatan      = cd['kecamatan']
                latest.kota_kabupaten = cd['kota_kabupaten']
                latest.provinsi       = cd['provinsi'] 
                latest.file_kk        = cd['file_kk']
                latest.file_ktp       = cd['file_ktp']
                latest.file_pengantar = cd['file_pengantar']
                latest.status         = 'pending'
                latest.catatan_admin  = None
                latest.save()
            else:
                MoveLetterRequest.objects.create(
                    user           = request.user,
                    keperluan      = cd['keperluan'],
                    jumlah_anggota = cd['jumlah_anggota'],
                    alamat_tujuan  = cd['alamat_tujuan'],
                    kelurahan      = cd['kelurahan'],
                    kecamatan      = cd['kecamatan'],
                    kota_kabupaten = cd['kota_kabupaten'],
                    provinsi       = cd['provinsi'],  
                    file_kk        = cd['file_kk'],
                    file_ktp       = cd['file_ktp'],
                    file_pengantar = cd['file_pengantar'],
                )
            return redirect('service:move_letter')

        # Form tidak valid — render ulang dengan error
        return render(request, 'service/forms/move_letter.html', _move_ctx(
            profile, profile_complete,
            is_pending_view, is_rejected_view, is_approved_view,
            latest, form,
        ))

    # ── GET ───────────────────────────────────────────────────
    form = MoveLetterForm()
    return render(request, 'service/forms/move_letter.html', _move_ctx(
        profile, profile_complete,
        is_pending_view, is_rejected_view, is_approved_view,
        latest, form,
    ))


def _move_ctx(profile, profile_complete,
              is_pending, is_rejected, is_approved,
              latest, form):
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

# ─────────────────────────────────────────────────────────────
# Unduh PDF Surat Pindah
# ─────────────────────────────────────────────────────────────

@login_required
def download_move_letter_pdf(request, ref):
    letter = get_object_or_404(
        MoveLetterRequest,
        reference_number=ref,
        user=request.user,
        status='approved',
    )

    from .utils.pdf_move_letter import generate_move_letter_pdf
    buffer = generate_move_letter_pdf(letter)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="surat-pindah-{letter.reference_number}.pdf"'
    )
    return response

# ─────────────────────────────────────────────────────────────
# Surat Domisili
# ─────────────────────────────────────────────────────────────

@login_required
def domicile_letter_view(request):
    profile          = _get_profile(request.user)
    profile_complete = _is_profile_complete(profile)

    latest = DomicileLetterRequest.objects.filter(
        user=request.user
    ).order_by('-created_at').first()

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
                latest.keperluan             = cd['keperluan']
                latest.tujuan_instansi       = cd['tujuan_instansi']
                latest.status_tempat_tinggal = cd['status_tempat_tinggal']
                latest.lama_tinggal_tahun    = cd['lama_tinggal_tahun']
                latest.lama_tinggal_bulan    = cd['lama_tinggal_bulan']
                latest.file_kk               = cd['file_kk']
                latest.file_ktp              = cd['file_ktp']
                latest.file_pengantar        = cd['file_pengantar']
                latest.status                = 'pending'
                latest.catatan_admin         = None
                latest.save()
            else:
                DomicileLetterRequest.objects.create(
                    user                  = request.user,
                    keperluan             = cd['keperluan'],
                    tujuan_instansi       = cd['tujuan_instansi'],
                    status_tempat_tinggal = cd['status_tempat_tinggal'],
                    lama_tinggal_tahun    = cd['lama_tinggal_tahun'],
                    lama_tinggal_bulan    = cd['lama_tinggal_bulan'],
                    file_kk               = cd['file_kk'],
                    file_ktp              = cd['file_ktp'],
                    file_pengantar        = cd['file_pengantar'],
                )
            return redirect('service:domicile_letter')

        return render(request, 'service/forms/domicile_letter.html', _domicile_ctx(
            profile, profile_complete,
            is_pending_view, is_rejected_view, is_approved_view,
            latest, form,
        ))

    form = DomicileLetterForm()
    return render(request, 'service/forms/domicile_letter.html', _domicile_ctx(
        profile, profile_complete,
        is_pending_view, is_rejected_view, is_approved_view,
        latest, form,
    ))


def _domicile_ctx(profile, profile_complete,
                   is_pending, is_rejected, is_approved,
                   latest, form):
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

# ─────────────────────────────────────────────────────────────
# Unduh PDF Surat Domisili
# ─────────────────────────────────────────────────────────────

@login_required
def download_domicile_letter_pdf(request, ref):
    letter = get_object_or_404(
        DomicileLetterRequest,
        reference_number=ref,
        user=request.user,
        status='approved',
    )

    from .utils.pdf_domicile_letter import generate_domicile_letter_pdf
    buffer = generate_domicile_letter_pdf(letter)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="surat-domisili-{letter.reference_number}.pdf"'
    )
    return response

# ─────────────────────────────────────────────────────────────
# Surat Kematian
# ─────────────────────────────────────────────────────────────

@login_required
def death_letter_view(request):
    profile          = _get_profile(request.user)
    profile_complete = _is_profile_complete(profile)

    latest = DeathLetterRequest.objects.filter(
        user=request.user
    ).order_by('-created_at').first()

    is_pending_view  = bool(latest and latest.status == 'pending')
    is_rejected_view = bool(latest and latest.status == 'rejected')
    is_approved_view = bool(latest and latest.status == 'approved')

    buat_baru = (request.GET.get('baru') == '1' or request.POST.get('baru') == '1')
    if buat_baru and is_approved_view:
        is_approved_view = False
        latest = None

    # ── POST ──────────────────────────────────────────────────
    if request.method == 'POST':
        if not profile_complete:
            return redirect('service:death_letter')
        if is_pending_view:
            return redirect('service:death_letter')

        form = DeathLetterForm(request.POST, request.FILES)

        if form.is_valid():
            cd = form.cleaned_data
            if is_rejected_view and latest:
                latest.nama_almarhum     = cd['nama_almarhum']
                latest.nik_almarhum      = cd['nik_almarhum']
                latest.jenis_kelamin     = cd['jenis_kelamin']
                latest.tempat_lahir      = cd['tempat_lahir']
                latest.tanggal_lahir     = cd['tanggal_lahir']
                latest.tanggal_kematian  = cd['tanggal_kematian']
                latest.tempat_kematian   = cd['tempat_kematian']
                latest.penyebab_kematian = cd['penyebab_kematian']
                latest.hubungan_pelapor  = cd['hubungan_pelapor']
                latest.file_kk           = cd['file_kk']
                latest.file_ktp_almarhum = cd['file_ktp_almarhum']
                if cd.get('file_surat_dokter'):
                    latest.file_surat_dokter = cd['file_surat_dokter']
                latest.status        = 'pending'
                latest.catatan_admin = None
                latest.save()
            else:
                kwargs = dict(
                    user             = request.user,
                    nama_almarhum    = cd['nama_almarhum'],
                    nik_almarhum     = cd['nik_almarhum'],
                    jenis_kelamin    = cd['jenis_kelamin'],
                    tempat_lahir     = cd['tempat_lahir'],
                    tanggal_lahir    = cd['tanggal_lahir'],
                    tanggal_kematian = cd['tanggal_kematian'],
                    tempat_kematian  = cd['tempat_kematian'],
                    penyebab_kematian= cd['penyebab_kematian'],
                    hubungan_pelapor = cd['hubungan_pelapor'],
                    file_kk          = cd['file_kk'],
                    file_ktp_almarhum= cd['file_ktp_almarhum'],
                )
                if cd.get('file_surat_dokter'):
                    kwargs['file_surat_dokter'] = cd['file_surat_dokter']
                DeathLetterRequest.objects.create(**kwargs)
            return redirect('service:death_letter')

        return render(request, 'service/forms/death_letter.html', _death_ctx(
            profile, profile_complete,
            is_pending_view, is_rejected_view, is_approved_view,
            latest, form,
        ))

    # ── GET ───────────────────────────────────────────────────
    form = DeathLetterForm()
    return render(request, 'service/forms/death_letter.html', _death_ctx(
        profile, profile_complete,
        is_pending_view, is_rejected_view, is_approved_view,
        latest, form,
    ))


def _death_ctx(profile, profile_complete,
               is_pending, is_rejected, is_approved,
               latest, form):
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


# ─────────────────────────────────────────────────────────────
# Unduh PDF Surat Kematian
# ─────────────────────────────────────────────────────────────

@login_required
def download_death_letter_pdf(request, ref):
    letter = get_object_or_404(
        DeathLetterRequest,
        reference_number=ref,
        user=request.user,
        status='approved',
    )

    from .utils.pdf_death_letter import generate_death_letter_pdf
    buffer = generate_death_letter_pdf(letter)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="surat-kematian-{letter.reference_number}.pdf"'
    )
    return response

# ─────────────────────────────────────────────────────────────
# Surat Kelahiran
# ─────────────────────────────────────────────────────────────

@login_required
def birth_letter_view(request):
    profile          = _get_profile(request.user)
    profile_complete = _is_profile_complete(profile)

    latest = BirthLetterRequest.objects.filter(
        user=request.user
    ).order_by('-created_at').first()

    is_pending_view  = bool(latest and latest.status == 'pending')
    is_rejected_view = bool(latest and latest.status == 'rejected')
    is_approved_view = bool(latest and latest.status == 'approved')

    buat_baru = (request.GET.get('baru') == '1' or request.POST.get('baru') == '1')
    if buat_baru and is_approved_view:
        is_approved_view = False
        latest = None

    # ── POST ──────────────────────────────────────────────────
    if request.method == 'POST':
        if not profile_complete:
            return redirect('service:birth_letter')
        if is_pending_view:
            return redirect('service:birth_letter')

        form = BirthLetterForm(request.POST, request.FILES)

        if form.is_valid():
            cd = form.cleaned_data
            if is_rejected_view and latest:
                latest.nama_bayi          = cd['nama_bayi']
                latest.jenis_kelamin_bayi = cd['jenis_kelamin_bayi']
                latest.tanggal_lahir_bayi = cd['tanggal_lahir_bayi']
                latest.tempat_lahir_bayi  = cd['tempat_lahir_bayi']
                latest.anak_ke            = cd['anak_ke']
                latest.nama_ayah          = cd['nama_ayah']
                latest.nik_ayah           = cd['nik_ayah']
                latest.nama_ibu           = cd['nama_ibu']
                latest.nik_ibu            = cd['nik_ibu']
                latest.file_kk            = cd['file_kk']
                latest.file_ktp_ayah      = cd['file_ktp_ayah']
                latest.file_ktp_ibu       = cd['file_ktp_ibu']
                if cd.get('file_surat_rs'):
                    latest.file_surat_rs  = cd['file_surat_rs']
                latest.status        = 'pending'
                latest.catatan_admin = None
                latest.save()
            else:
                kwargs = dict(
                    user              = request.user,
                    nama_bayi         = cd['nama_bayi'],
                    jenis_kelamin_bayi= cd['jenis_kelamin_bayi'],
                    tanggal_lahir_bayi= cd['tanggal_lahir_bayi'],
                    tempat_lahir_bayi = cd['tempat_lahir_bayi'],
                    anak_ke           = cd['anak_ke'],
                    nama_ayah         = cd['nama_ayah'],
                    nik_ayah          = cd['nik_ayah'],
                    nama_ibu          = cd['nama_ibu'],
                    nik_ibu           = cd['nik_ibu'],
                    file_kk           = cd['file_kk'],
                    file_ktp_ayah     = cd['file_ktp_ayah'],
                    file_ktp_ibu      = cd['file_ktp_ibu'],
                )
                if cd.get('file_surat_rs'):
                    kwargs['file_surat_rs'] = cd['file_surat_rs']
                BirthLetterRequest.objects.create(**kwargs)
            return redirect('service:birth_letter')

        return render(request, 'service/forms/birth_letter.html', _birth_ctx(
            profile, profile_complete,
            is_pending_view, is_rejected_view, is_approved_view,
            latest, form,
        ))

    # ── GET ───────────────────────────────────────────────────
    form = BirthLetterForm()
    return render(request, 'service/forms/birth_letter.html', _birth_ctx(
        profile, profile_complete,
        is_pending_view, is_rejected_view, is_approved_view,
        latest, form,
    ))


def _birth_ctx(profile, profile_complete,
               is_pending, is_rejected, is_approved,
               latest, form):
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


# ─────────────────────────────────────────────────────────────
# Unduh PDF Surat Kelahiran
# ─────────────────────────────────────────────────────────────

@login_required
def download_birth_letter_pdf(request, ref):
    letter = get_object_or_404(
        BirthLetterRequest,
        reference_number=ref,
        user=request.user,
        status='approved',
    )

    from .utils.pdf_birth_letter import generate_birth_letter_pdf
    buffer = generate_birth_letter_pdf(letter)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="surat-kelahiran-{letter.reference_number}.pdf"'
    )
    return response

# ─────────────────────────────────────────────────────────────
# Surat Tidak Mampu
# ─────────────────────────────────────────────────────────────
 
@login_required
def poverty_letter_view(request):
    profile          = _get_profile(request.user)
    profile_complete = _is_profile_complete(profile)
 
    latest = PovertyLetterRequest.objects.filter(
        user=request.user
    ).order_by('-created_at').first()
 
    is_pending_view  = bool(latest and latest.status == 'pending')
    is_rejected_view = bool(latest and latest.status == 'rejected')
    is_approved_view = bool(latest and latest.status == 'approved')
 
    buat_baru = (request.GET.get('baru') == '1' or request.POST.get('baru') == '1')
    if buat_baru and is_approved_view:
        is_approved_view = False
        latest = None
 
    # ── POST ──────────────────────────────────────────────────
    if request.method == 'POST':
        if not profile_complete:
            return redirect('service:poverty_letter')
        if is_pending_view:
            return redirect('service:poverty_letter')
 
        form = PovertyLetterForm(request.POST, request.FILES)
 
        if form.is_valid():
            cd = form.cleaned_data
            if is_rejected_view and latest:
                latest.keperluan         = cd['keperluan']
                latest.keperluan_lain    = cd.get('keperluan_lain', '')
                latest.tujuan_instansi   = cd['tujuan_instansi']
                latest.penghasilan       = cd['penghasilan']
                latest.jumlah_tanggungan = cd['jumlah_tanggungan']
                latest.file_kk           = cd['file_kk']
                latest.file_ktp          = cd['file_ktp']
                latest.file_pengantar    = cd['file_pengantar']
                if cd.get('file_pendukung'):
                    latest.file_pendukung = cd['file_pendukung']
                latest.status        = 'pending'
                latest.catatan_admin = None
                latest.save()
            else:
                kwargs = dict(
                    user             = request.user,
                    keperluan        = cd['keperluan'],
                    keperluan_lain   = cd.get('keperluan_lain', ''),
                    tujuan_instansi  = cd['tujuan_instansi'],
                    penghasilan      = cd['penghasilan'],
                    jumlah_tanggungan= cd['jumlah_tanggungan'],
                    file_kk          = cd['file_kk'],
                    file_ktp         = cd['file_ktp'],
                    file_pengantar   = cd['file_pengantar'],
                )
                if cd.get('file_pendukung'):
                    kwargs['file_pendukung'] = cd['file_pendukung']
                PovertyLetterRequest.objects.create(**kwargs)
            return redirect('service:poverty_letter')
 
        return render(request, 'service/forms/poverty_letter.html', _poverty_ctx(
            profile, profile_complete,
            is_pending_view, is_rejected_view, is_approved_view,
            latest, form,
        ))
 
    # ── GET ───────────────────────────────────────────────────
    form = PovertyLetterForm()
    return render(request, 'service/forms/poverty_letter.html', _poverty_ctx(
        profile, profile_complete,
        is_pending_view, is_rejected_view, is_approved_view,
        latest, form,
    ))
 
 
def _poverty_ctx(profile, profile_complete,
                 is_pending, is_rejected, is_approved,
                 latest, form):
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
 
 
# ─────────────────────────────────────────────────────────────
# Unduh PDF Surat Tidak Mampu
# ─────────────────────────────────────────────────────────────
 
@login_required
def download_poverty_letter_pdf(request, ref):
    letter = get_object_or_404(
        PovertyLetterRequest,
        reference_number=ref,
        user=request.user,
        status='approved',
    )
 
    from .utils.pdf_poverty_letter import generate_poverty_letter_pdf
    buffer = generate_poverty_letter_pdf(letter)
 
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="surat-tidak-mampu-{letter.reference_number}.pdf"'
    )
    return response

# ─────────────────────────────────────────────────────────────
# Surat Keterangan Usaha
# ─────────────────────────────────────────────────────────────
 
def business_letter_view(request):  # tambahkan @login_required
    profile          = _get_profile(request.user)
    profile_complete = _is_profile_complete(profile)
 
    latest = BusinessLetterRequest.objects.filter(
        user=request.user
    ).order_by('-created_at').first()
 
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
                latest.nama_usaha       = cd['nama_usaha']
                latest.jenis_usaha      = cd['jenis_usaha']
                latest.jenis_usaha_lain = cd.get('jenis_usaha_lain', '')
                latest.alamat_usaha     = cd['alamat_usaha']
                latest.lama_usaha_tahun = cd['lama_usaha_tahun']
                latest.omset_perbulan   = cd['omset_perbulan']
                latest.keperluan        = cd['keperluan']
                latest.keperluan_lain   = cd.get('keperluan_lain', '')
                latest.tujuan_instansi  = cd['tujuan_instansi']
                latest.file_ktp         = cd['file_ktp']
                latest.file_kk          = cd['file_kk']
                if cd.get('file_foto_usaha'):
                    latest.file_foto_usaha = cd['file_foto_usaha']
                latest.status        = 'pending'
                latest.catatan_admin = None
                latest.save()
            else:
                kwargs = dict(
                    user            = request.user,
                    nama_usaha      = cd['nama_usaha'],
                    jenis_usaha     = cd['jenis_usaha'],
                    jenis_usaha_lain= cd.get('jenis_usaha_lain', ''),
                    alamat_usaha    = cd['alamat_usaha'],
                    lama_usaha_tahun= cd['lama_usaha_tahun'],
                    omset_perbulan  = cd['omset_perbulan'],
                    keperluan       = cd['keperluan'],
                    keperluan_lain  = cd.get('keperluan_lain', ''),
                    tujuan_instansi = cd['tujuan_instansi'],
                    file_ktp        = cd['file_ktp'],
                    file_kk         = cd['file_kk'],
                )
                if cd.get('file_foto_usaha'):
                    kwargs['file_foto_usaha'] = cd['file_foto_usaha']
                BusinessLetterRequest.objects.create(**kwargs)
            return redirect('service:business_letter')
 
        return render(request, 'service/forms/business_letter.html', _business_ctx(
            profile, profile_complete,
            is_pending_view, is_rejected_view, is_approved_view,
            latest, form,
        ))
 
    form = BusinessLetterForm()
    return render(request, 'service/forms/business_letter.html', _business_ctx(
        profile, profile_complete,
        is_pending_view, is_rejected_view, is_approved_view,
        latest, form,
    ))
 
 
def _business_ctx(profile, profile_complete,
                  is_pending, is_rejected, is_approved,
                  latest, form):
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
 
# ─────────────────────────────────────────────────────────────
# Unduh PDF Surat Keterangan Usaha
# ─────────────────────────────────────────────────────────────

@login_required
def download_business_letter_pdf(request, ref):  # tambahkan @login_required
    letter = get_object_or_404(
        BusinessLetterRequest,
        reference_number=ref,
        user=request.user,
        status='approved',
    )
 
    from .utils.pdf_business_letter import generate_business_letter_pdf
    buffer = generate_business_letter_pdf(letter)
 
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="surat-keterangan-usaha-{letter.reference_number}.pdf"'
    )
    return response

# ─────────────────────────────────────────────────────────────
# Surat Pengantar
# ─────────────────────────────────────────────────────────────

@login_required
def intro_letter_view(request):
    profile          = _get_profile(request.user)
    profile_complete = _is_profile_complete(profile)

    latest = IntroLetterRequest.objects.filter(
        user=request.user
    ).order_by('-created_at').first()

    is_pending_view  = bool(latest and latest.status == 'pending')
    is_rejected_view = bool(latest and latest.status == 'rejected')
    is_approved_view = bool(latest and latest.status == 'approved')

    buat_baru = (request.GET.get('baru') == '1' or request.POST.get('baru') == '1')
    if buat_baru and is_approved_view:
        is_approved_view = False
        latest = None

    # ── POST ──────────────────────────────────────────────────
    if request.method == 'POST':
        if not profile_complete:
            return redirect('service:intro_letter')
        if is_pending_view:
            return redirect('service:intro_letter')

        form = IntroLetterForm(request.POST, request.FILES)

        if form.is_valid():
            cd = form.cleaned_data
            if is_rejected_view and latest:
                latest.keperluan            = cd['keperluan']
                latest.keperluan_lain       = cd.get('keperluan_lain', '')
                latest.tujuan_instansi      = cd['tujuan_instansi']
                latest.keterangan_tambahan  = cd.get('keterangan_tambahan', '')
                latest.file_ktp             = cd['file_ktp']
                latest.file_kk              = cd['file_kk']
                if cd.get('file_pendukung'):
                    latest.file_pendukung = cd['file_pendukung']
                latest.status        = 'pending'
                latest.catatan_admin = None
                latest.save()
            else:
                kwargs = dict(
                    user                = request.user,
                    keperluan           = cd['keperluan'],
                    keperluan_lain      = cd.get('keperluan_lain', ''),
                    tujuan_instansi     = cd['tujuan_instansi'],
                    keterangan_tambahan = cd.get('keterangan_tambahan', ''),
                    file_ktp            = cd['file_ktp'],
                    file_kk             = cd['file_kk'],
                )
                if cd.get('file_pendukung'):
                    kwargs['file_pendukung'] = cd['file_pendukung']
                IntroLetterRequest.objects.create(**kwargs)
            return redirect('service:intro_letter')

        return render(request, 'service/forms/intro_letter.html', _intro_ctx(
            profile, profile_complete,
            is_pending_view, is_rejected_view, is_approved_view,
            latest, form,
        ))

    # ── GET ───────────────────────────────────────────────────
    form = IntroLetterForm()
    return render(request, 'service/forms/intro_letter.html', _intro_ctx(
        profile, profile_complete,
        is_pending_view, is_rejected_view, is_approved_view,
        latest, form,
    ))


def _intro_ctx(profile, profile_complete,
               is_pending, is_rejected, is_approved,
               latest, form):
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


# ─────────────────────────────────────────────────────────────
# Unduh PDF Surat Pengantar
# ─────────────────────────────────────────────────────────────

@login_required
def download_intro_letter_pdf(request, ref):
    letter = get_object_or_404(
        IntroLetterRequest,
        reference_number=ref,
        user=request.user,
        status='approved',
    )

    from .utils.pdf_intro_letter import generate_intro_letter_pdf
    buffer = generate_intro_letter_pdf(letter)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="surat-pengantar-{letter.reference_number}.pdf"'
    )
    return response