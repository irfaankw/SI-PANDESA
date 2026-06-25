# welfare/views.py
from django.shortcuts import render, redirect, get_object_or_404
from core.decorators import verified_required
from django.contrib import messages
from django.urls import reverse
from .models import UMKM, Produk, ProgramBansos, PengajuanBansos
from .forms import UMKMForm, ProdukForm, PengajuanBansosForm


def _get_profil_data(user):
    nama = user.get_full_name() or user.username
    no_hp = ''
    try:
        no_hp = user.profile.no_hp or ''
    except Exception:
        pass
    return nama, no_hp


def _get_profile(user):
    try:
        return user.profile
    except Exception:
        return None


@verified_required
def kesejahteraan_view(request):
    profile     = _get_profile(request.user)
    is_verified = profile.is_verified if profile else False

    # ── Data UMKM ──
    umkm_existing = None
    if hasattr(request.user, 'umkm'):
        umkm_existing = request.user.umkm

    nama_pemilik, no_hp = _get_profil_data(request.user)

    # ── Data Bansos ──
    program_list     = ProgramBansos.objects.filter(aktif=True)
    pengajuan_user   = PengajuanBansos.objects.filter(
        user=request.user
    ).select_related('program')
    sudah_daftar_ids = set(pengajuan_user.values_list('program_id', flat=True))
    bansos_form      = PengajuanBansosForm(user=request.user)
    umkm_form        = UMKMForm()

    _url_bansos = reverse('welfare:kesejahteraan') + '?tab=bansos'
    _url_umkm   = reverse('welfare:kesejahteraan') + '?tab=umkm'

    # ── Handle POST Bansos ──
    if request.method == 'POST' and request.POST.get('form_type') == 'bansos':
        if not is_verified:
            messages.error(request, 'Akun Anda belum diverifikasi.')
            return redirect(_url_bansos)

        bansos_form = PengajuanBansosForm(request.POST, user=request.user)
        if bansos_form.is_valid():
            pengajuan      = bansos_form.save(commit=False)
            pengajuan.user = request.user
            pengajuan.save()
            messages.success(
                request,
                f'Pengajuan "{pengajuan.program.nama}" berhasil dikirim!'
            )
            return redirect(_url_bansos)
        else:
            for field, errors in bansos_form.errors.items():
                for error in errors:
                    messages.error(request, error)
            return redirect(_url_bansos)

    # ── Handle POST UMKM ──
    if request.method == 'POST' and request.POST.get('form_type') == 'umkm':
        if not is_verified:
            messages.error(request, 'Akun Anda belum diverifikasi.')
            return redirect(_url_umkm)

        if umkm_existing:
            messages.error(request, 'Anda sudah memiliki UMKM terdaftar.')
            return redirect(_url_umkm)

        umkm_form = UMKMForm(request.POST)
        if umkm_form.is_valid():
            umkm         = umkm_form.save(commit=False)
            umkm.pemilik = request.user
            umkm.save()
            messages.success(
                request,
                f'UMKM "{umkm.nama_usaha}" berhasil didaftarkan! '
                f'No. Pengajuan: {umkm.nomor_pengajuan}.'
            )
            return redirect(_url_umkm)
        else:
            for field, errors in umkm_form.errors.items():
                for error in errors:
                    messages.error(request, error)

    return render(request, 'welfare/kesejahteraan.html', {
        'title':            'Kesejahteraan Warga',
        'active_tab':       'kesejahteraan',
        'form':             umkm_form,
        'nama_pemilik':     nama_pemilik,
        'no_hp':            no_hp,
        'umkm_existing':    umkm_existing,
        'tab':              request.GET.get('tab', 'umkm'),
        'is_verified':      is_verified,
        'profile':          profile,
        'program_list':     program_list,
        'pengajuan_user':   pengajuan_user,
        'sudah_daftar_ids': sudah_daftar_ids,
        'bansos_form':      bansos_form,
    })


@verified_required
def batalkan_bansos_view(request, pk):
    pengajuan = get_object_or_404(
        PengajuanBansos, pk=pk, user=request.user, status='pending'
    )
    if request.method == 'POST':
        nama = pengajuan.program.nama
        pengajuan.delete()
        messages.success(request, f'Pengajuan "{nama}" berhasil dibatalkan.')
    return redirect(reverse('welfare:kesejahteraan') + '?tab=bansos')


@verified_required
def kelola_toko_view(request):
    try:
        umkm        = UMKM.objects.get(pemilik=request.user)
        produk_list = umkm.produk.all()
    except UMKM.DoesNotExist:
        umkm        = None
        produk_list = []

    return render(request, 'welfare/kelola_toko.html', {
        'title'      : f'Kelola Toko — {umkm.nama_usaha}' if umkm else 'Kelola Toko',
        'umkm'       : umkm,
        'produk_list': produk_list,
    })


@verified_required
def tambah_produk_view(request):
    umkm = get_object_or_404(UMKM, pemilik=request.user)

    if umkm.status != 'aktif':
        messages.error(request, 'UMKM Anda belum aktif. Tunggu verifikasi admin.')
        return redirect('welfare:kelola_toko')

    if request.method == 'POST':
        form = ProdukForm(request.POST, request.FILES)
        if form.is_valid():
            produk      = form.save(commit=False)
            produk.umkm = umkm
            produk.save()
            messages.success(request, f'Produk "{produk.nama}" berhasil ditambahkan!')
            return redirect('welfare:kelola_toko')
    else:
        form = ProdukForm()

    return render(request, 'welfare/tambah_produk.html', {
        'title': 'Tambah Produk',
        'umkm' : umkm,
        'form' : form,
    })


@verified_required
def edit_produk_view(request, produk_id):
    umkm   = get_object_or_404(UMKM, pemilik=request.user)
    produk = get_object_or_404(Produk, id=produk_id, umkm=umkm)

    if request.method == 'POST':
        form = ProdukForm(request.POST, request.FILES, instance=produk)
        if form.is_valid():
            form.save()
            messages.success(request, f'Produk "{produk.nama}" berhasil diperbarui!')
            return redirect('welfare:kelola_toko')
    else:
        form = ProdukForm(instance=produk)

    return render(request, 'welfare/tambah_produk.html', {
        'title' : 'Edit Produk',
        'umkm'  : umkm,
        'form'  : form,
        'produk': produk,
    })


@verified_required
def hapus_produk_view(request, produk_id):
    umkm   = get_object_or_404(UMKM, pemilik=request.user)
    produk = get_object_or_404(Produk, id=produk_id, umkm=umkm)

    if request.method == 'POST':
        nama = produk.nama
        produk.delete()
        messages.success(request, f'Produk "{nama}" berhasil dihapus.')

    return redirect('welfare:kelola_toko')