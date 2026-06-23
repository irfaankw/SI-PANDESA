# welfare/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404
from .models import UMKM, Produk
from .forms import UMKMForm, ProdukForm


def _get_profil_data(user):
    nama = user.get_full_name() or user.username
    no_hp = ''
    try:
        no_hp = user.profile.no_hp or ''
    except Exception:
        pass
    return nama, no_hp


@login_required
def kesejahteraan_view(request):
    umkm_existing = None
    if hasattr(request.user, 'umkm'):
        umkm_existing = request.user.umkm

    nama_pemilik, no_hp = _get_profil_data(request.user)

    if request.method == 'POST':
        if umkm_existing:
            messages.error(request, 'Anda sudah memiliki UMKM terdaftar.')
            return redirect('welfare:kesejahteraan')

        form = UMKMForm(request.POST)
        if form.is_valid():
            umkm         = form.save(commit=False)
            umkm.pemilik = request.user
            umkm.save()
            messages.success(
                request,
                f'UMKM "{umkm.nama_usaha}" berhasil didaftarkan! '
                f'No. Pengajuan: {umkm.nomor_pengajuan}.'
            )
            return redirect('welfare:kesejahteraan')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        form = UMKMForm()

    return render(request, 'welfare/kesejahteraan.html', {
        'title':         'Kesejahteraan Warga',
        'active_tab':    'kesejahteraan',
        'form':          form,
        'nama_pemilik':  nama_pemilik,
        'no_hp':         no_hp,
        'umkm_existing': umkm_existing,
        'tab':           request.GET.get('tab', 'umkm'),
    })


@login_required
def kelola_toko_view(request):
    # Menggunakan try-except blocks standar Django agar aman jika objek tidak ditemukan
    try:
        # Menggunakan .objects.get() dengan benar melewati ORM Django
        umkm = UMKM.objects.get(pemilik=request.user)
        produk_list = umkm.produk.all()
    except UMKM.DoesNotExist:
        # Jika user belum mendaftar UMKM, set nilainya ke None agar dibaca kondisi {% if not umkm %} di template
        umkm = None
        produk_list = []

    return render(request, 'welfare/kelola_toko.html', {
        'title': f'Kelola Toko — {umkm.nama_usaha}' if umkm else 'Kelola Toko',
        'umkm': umkm,
        'produk_list': produk_list,
    })

@login_required
def tambah_produk_view(request):
    umkm = get_object_or_404(UMKM, pemilik=request.user)

    # Hanya UMKM aktif yang bisa tambah produk
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
        'umkm':  umkm,
        'form':  form,
    })


@login_required
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
        'title':  'Edit Produk',
        'umkm':   umkm,
        'form':   form,
        'produk': produk,   # kalau ada berarti mode edit
    })


@login_required
def hapus_produk_view(request, produk_id):
    umkm   = get_object_or_404(UMKM, pemilik=request.user)
    produk = get_object_or_404(Produk, id=produk_id, umkm=umkm)

    if request.method == 'POST':
        nama = produk.nama
        produk.delete()
        messages.success(request, f'Produk "{nama}" berhasil dihapus.')

    return redirect('welfare:kelola_toko')