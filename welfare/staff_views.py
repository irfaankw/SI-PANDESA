"""
welfare/staff_views.py
======================
Views Staff Desa untuk mengelola UMKM warga.

Disesuaikan dengan welfare/models.py yang asli:
- FK ke User pakai field 'pemilik' (bukan 'user')
- STATUS_CHOICES: 'pending', 'aktif', 'nonaktif'
  (tidak pakai 'approved'/'rejected' — disesuaikan jadi 'aktif'/'nonaktif')
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q

from core.decorators import staff_desa_required
from .models import UMKM, Produk


# ─────────────────────────────────────────────────────────────
# View 1 — Dashboard Kesejahteraan: ringkasan
# ─────────────────────────────────────────────────────────────

@staff_desa_required
def staff_welfare_dashboard(request):
    stats = {
        'total_umkm'  : UMKM.objects.count(),
        'umkm_pending': UMKM.objects.filter(status='pending').count(),
        'umkm_aktif'  : UMKM.objects.filter(status='aktif').count(),
        'umkm_nonaktif': UMKM.objects.filter(status='nonaktif').count(),
    }

    # 5 UMKM terbaru yang masih pending — untuk quick action di dashboard
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
            Q(nama_usaha__icontains=search_q)            |
            Q(pemilik__first_name__icontains=search_q)   |
            Q(pemilik__last_name__icontains=search_q)    |
            Q(pemilik__username__icontains=search_q)
        )

    umkm_list = list(qs)

    stats = {
        'total'    : UMKM.objects.count(),
        'pending'  : UMKM.objects.filter(status='pending').count(),
        'aktif'    : UMKM.objects.filter(status='aktif').count(),
        'nonaktif' : UMKM.objects.filter(status='nonaktif').count(),
    }

    return render(request, 'welfare/staff_umkm_list.html', {
        'umkm_list'    : umkm_list,
        'stats'        : stats,
        'status_filter': status_filter,
        'search_q'     : search_q,
    })


# ─────────────────────────────────────────────────────────────
# View 3 — Detail UMKM: lihat + aktifkan / nonaktifkan
# ─────────────────────────────────────────────────────────────

@staff_desa_required
def staff_umkm_detail(request, pk):
    # select_related ke pemilik dan profilnya, prefetch_related produk
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
            messages.success(
                request,
                f"UMKM '{umkm.nama_usaha}' berhasil diaktifkan. "
                f"Toko kini tampil di halaman Pasar Desa."
            )
            return redirect('welfare_staff:umkm_list')

        elif action == 'nonaktifkan':
            umkm.status = 'nonaktif'
            umkm.save()
            messages.success(
                request,
                f"UMKM '{umkm.nama_usaha}' telah dinonaktifkan."
            )
            return redirect('welfare_staff:umkm_list')

    produk_list = umkm.produk.all()

    return render(request, 'welfare/staff_umkm_detail.html', {
        'umkm'       : umkm,
        'produk_list': produk_list,
    })