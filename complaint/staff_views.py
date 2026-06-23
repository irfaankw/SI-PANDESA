# Views Staff Desa untuk mengelola pengaduan warga.

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, Count, Case, When, IntegerField

from core.decorators import staff_desa_required
from .models import ComplaintReport


@staff_desa_required
def staff_complaint_dashboard(request):
    status_filter = request.GET.get('status', 'all')
    search_q      = request.GET.get('q', '').strip()

    qs = ComplaintReport.objects.select_related('user', 'user__profile').order_by('-created_at')

    if status_filter != 'all':
        qs = qs.filter(status=status_filter)

    if search_q:
        qs = qs.filter(
            Q(user__first_name__icontains=search_q) |
            Q(user__last_name__icontains=search_q)  |
            Q(user__username__icontains=search_q)   |
            Q(judul__icontains=search_q)
        )

    complaints = list(qs)

    all_qs = ComplaintReport.objects
    stats = {
        'total'   : all_qs.count(),
        'pending' : all_qs.filter(status='pending').count(),
        'diproses': all_qs.filter(status='in_progress').count(),
        'selesai' : all_qs.filter(status='resolved').count(),
    }

    return render(request, 'complaint/staff_dashboard.html', {
        'complaints'   : complaints,
        'stats'        : stats,
        'status_filter': status_filter,
        'search_q'     : search_q,
    })


@staff_desa_required
def staff_complaint_detail(request, pk):
    complaint = get_object_or_404(
        ComplaintReport.objects.select_related('user', 'user__profile'),
        pk=pk,
    )

    if request.method == 'POST':
        new_status = request.POST.get('status', '').strip()
        tanggapan  = request.POST.get('tanggapan', '').strip()

        VALID_STATUS = ['pending', 'in_progress', 'resolved', 'rejected']
        if new_status and new_status in VALID_STATUS:
            complaint.status = new_status

        if tanggapan and hasattr(complaint, 'tanggapan_admin'):
            complaint.tanggapan_admin = tanggapan

        complaint.save()
        messages.success(request, f"Pengaduan #{complaint.pk} berhasil diperbarui.")
        return redirect('complaint_staff:dashboard')

    return render(request, 'complaint/staff_detail.html', {'complaint': complaint})