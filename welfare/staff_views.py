"""
welfare/staff_views.py
======================
Views Staff Desa untuk mengelola UMKM dan Bansos warga.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django import forms as django_forms

from core.decorators import staff_desa_required
from .models import UMKM, Produk, ProgramBansos, PengajuanBansos
from .forms import PengajuanBansosForm


# ─────────────────────────────────────────────────────────────
# Form Program Bansos (hanya dipakai di staff)
# ─────────────────────────────────────────────────────────────
_STAFF_INPUT = (
    "w-full px-4 py-3 border border-slate-200 rounded-xl "
    "focus:outline-none focus:ring-2 focus:ring-emerald-500 "
    "bg-white text-slate-800 text-sm"
)

class ProgramBansosForm(django_forms.ModelForm):
    class Meta:
        model  = ProgramBansos
        fields = ['nama', 'kategori', 'deskripsi', 'anggaran', 'kuota_penerima', 'aktif']
        widgets = {
            'nama'          : django_forms.TextInput(attrs={'class': _STAFF_INPUT, 'placeholder': 'Nama program'}),
            'kategori'      : django_forms.Select(attrs={'class': _STAFF_INPUT}),
            'deskripsi'     : django_forms.Textarea(attrs={'class': _STAFF_INPUT, 'rows': 3}),
            'anggaran'      : django_forms.NumberInput(attrs={'class': _STAFF_INPUT, 'placeholder': '0'}),
            'kuota_penerima': django_forms.NumberInput(attrs={'class': _STAFF_INPUT, 'placeholder': '0'}),
        }


# ─────────────────────────────────────────────────────────────
# View 1 — Dashboard Kesejahteraan (UMKM)
# ─────────────────────────────────────────────────────────────

@staff_desa_required
def staff_welfare_dashboard(request):
    stats = {
        'total_umkm'   : UMKM.objects.count(),
        'umkm_pending' : UMKM.objects.filter(status='pending').count(),
        'umkm_aktif'   : UMKM.objects.filter(status='aktif').count(),
        'umkm_nonaktif': UMKM.objects.filter(status='nonaktif').count(),
    }
    umkm_pending = list(
        UMKM.objects.filter(status='pending')
        .select_related('pemilik', 'pemilik__profile')
        .order_by('-created_at')[:5]
    )
    return render(request, 'welfare/staff_dashboard.html', {
        'stats'       : stats,
        'umkm_pending': umkm_pending,
    })


# ─────────────────────────────────────────────────────────────
# View 2 — Daftar semua UMKM
# ─────────────────────────────────────────────────────────────

@staff_desa_required
def staff_umkm_list(request):
    status_filter = request.GET.get('status', 'all')
    search_q      = request.GET.get('q', '').strip()

    qs = UMKM.objects.select_related('pemilik', 'pemilik__profile').order_by('-created_at')

    if status_filter != 'all':
        qs = qs.filter(status=status_filter)
    if search_q:
        qs = qs.filter(
            Q(nama_usaha__icontains=search_q)          |
            Q(pemilik__first_name__icontains=search_q) |
            Q(pemilik__last_name__icontains=search_q)  |
            Q(pemilik__username__icontains=search_q)
        )

    stats = {
        'total'    : UMKM.objects.count(),
        'pending'  : UMKM.objects.filter(status='pending').count(),
        'aktif'    : UMKM.objects.filter(status='aktif').count(),
        'nonaktif' : UMKM.objects.filter(status='nonaktif').count(),
    }
    return render(request, 'welfare/staff_umkm_list.html', {
        'umkm_list'    : list(qs),
        'stats'        : stats,
        'status_filter': status_filter,
        'search_q'     : search_q,
    })


# ─────────────────────────────────────────────────────────────
# View 3 — Detail UMKM
# ─────────────────────────────────────────────────────────────

@staff_desa_required
def staff_umkm_detail(request, pk):
    umkm = get_object_or_404(
        UMKM.objects
        .select_related('pemilik', 'pemilik__profile')
        .prefetch_related('produk'),
        pk=pk,
    )
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'aktifkan':
            umkm.status = 'aktif'
            umkm.save()
            messages.success(request, f"UMKM '{umkm.nama_usaha}' berhasil diaktifkan.")
            return redirect('welfare_staff:umkm_list')
        elif action == 'nonaktifkan':
            umkm.status = 'nonaktif'
            umkm.save()
            messages.success(request, f"UMKM '{umkm.nama_usaha}' telah dinonaktifkan.")
            return redirect('welfare_staff:umkm_list')

    return render(request, 'welfare/staff_umkm_detail.html', {
        'umkm'       : umkm,
        'produk_list': umkm.produk.all(),
    })


# ─────────────────────────────────────────────────────────────
# View 4 — Dashboard Bansos
# ─────────────────────────────────────────────────────────────

@staff_desa_required
def staff_bansos_dashboard(request):
    stats = {
        'total_program'  : ProgramBansos.objects.count(),
        'program_aktif'  : ProgramBansos.objects.filter(aktif=True).count(),
        'total_pengajuan': PengajuanBansos.objects.count(),
        'pending'        : PengajuanBansos.objects.filter(status='pending').count(),
        'disetujui'      : PengajuanBansos.objects.filter(status='disetujui').count(),
        'ditolak'        : PengajuanBansos.objects.filter(status='ditolak').count(),
    }
    program_list   = ProgramBansos.objects.all()
    pengajuan_baru = PengajuanBansos.objects.filter(
        status='pending'
    ).select_related('user', 'program', 'user__profile').order_by('-created_at')[:5]

    return render(request, 'welfare/staff_bansos_dashboard.html', {
        'stats'         : stats,
        'program_list'  : program_list,
        'pengajuan_baru': pengajuan_baru,
    })


# ─────────────────────────────────────────────────────────────
# View 5 — Tambah Program Bansos
# ─────────────────────────────────────────────────────────────

@staff_desa_required
def staff_program_tambah(request):
    form = ProgramBansosForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        program = form.save()
        messages.success(request, f'Program "{program.nama}" berhasil ditambahkan.')
        return redirect('welfare_staff:bansos_dashboard')
    return render(request, 'welfare/staff_program_form.html', {
        'form' : form,
        'title': 'Tambah Program Bansos',
    })


# ─────────────────────────────────────────────────────────────
# View 6 — Edit Program Bansos
# ─────────────────────────────────────────────────────────────

@staff_desa_required
def staff_program_edit(request, pk):
    program = get_object_or_404(ProgramBansos, pk=pk)
    form    = ProgramBansosForm(request.POST or None, instance=program)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Program "{program.nama}" berhasil diperbarui.')
        return redirect('welfare_staff:bansos_dashboard')
    return render(request, 'welfare/staff_program_form.html', {
        'form'   : form,
        'title'  : 'Edit Program Bansos',
        'program': program,
    })


# ─────────────────────────────────────────────────────────────
# View 7 — Toggle Aktif/Nonaktif Program
# ─────────────────────────────────────────────────────────────

@staff_desa_required
def staff_program_toggle(request, pk):
    program = get_object_or_404(ProgramBansos, pk=pk)
    if request.method == 'POST':
        program.aktif = not program.aktif
        program.save()
        status = 'diaktifkan' if program.aktif else 'dinonaktifkan'
        messages.success(request, f'Program "{program.nama}" berhasil {status}.')
    return redirect('welfare_staff:bansos_dashboard')


# ─────────────────────────────────────────────────────────────
# View 8 — Daftar Pengajuan Bansos
# ─────────────────────────────────────────────────────────────

@staff_desa_required
def staff_pengajuan_list(request):
    status_filter = request.GET.get('status', 'all')
    search_q      = request.GET.get('q', '').strip()

    qs = PengajuanBansos.objects.select_related(
        'user', 'program', 'user__profile'
    ).order_by('-created_at')

    if status_filter != 'all':
        qs = qs.filter(status=status_filter)
    if search_q:
        qs = qs.filter(
            Q(user__first_name__icontains=search_q) |
            Q(user__last_name__icontains=search_q)  |
            Q(user__username__icontains=search_q)   |
            Q(program__nama__icontains=search_q)
        )

    return render(request, 'welfare/staff_pengajuan_list.html', {
        'pengajuan_list': list(qs),
        'status_filter' : status_filter,
        'search_q'      : search_q,
        'stats': {
            'total'    : PengajuanBansos.objects.count(),
            'pending'  : PengajuanBansos.objects.filter(status='pending').count(),
            'disetujui': PengajuanBansos.objects.filter(status='disetujui').count(),
            'ditolak'  : PengajuanBansos.objects.filter(status='ditolak').count(),
        },
    })


# ─────────────────────────────────────────────────────────────
# View 9 — Detail Pengajuan Bansos
# ─────────────────────────────────────────────────────────────

@staff_desa_required
def staff_pengajuan_detail(request, pk):
    pengajuan = get_object_or_404(
        PengajuanBansos.objects.select_related('user', 'program', 'user__profile'),
        pk=pk,
    )
    if request.method == 'POST':
        action  = request.POST.get('action')
        catatan = request.POST.get('catatan_staff', '').strip()

        if action == 'setujui':
            pengajuan.status        = 'disetujui'
            pengajuan.catatan_staff = catatan
            pengajuan.save()
            messages.success(request, f'Pengajuan {pengajuan.nama_pemohon} disetujui.')
        elif action == 'tolak':
            pengajuan.status        = 'ditolak'
            pengajuan.catatan_staff = catatan
            pengajuan.save()
            messages.success(request, f'Pengajuan {pengajuan.nama_pemohon} ditolak.')

        return redirect('welfare_staff:pengajuan_list')

    return render(request, 'welfare/staff_pengajuan_detail.html', {
        'pengajuan': pengajuan,
    })