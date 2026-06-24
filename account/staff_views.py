from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q

from core.decorators import staff_desa_required
from .models import UserProfile


@staff_desa_required
def staff_profile_dashboard(request):
    status_filter = request.GET.get('status', 'all')
    search_q      = request.GET.get('q', '').strip()

    qs = UserProfile.objects.select_related('user').order_by('-created_at')

    if status_filter != 'all':
        qs = qs.filter(status_verifikasi=status_filter)

    if search_q:
        qs = qs.filter(
            Q(user__first_name__icontains=search_q) |
            Q(user__last_name__icontains=search_q)  |
            Q(user__username__icontains=search_q)   |
            Q(user__email__icontains=search_q)      |
            Q(nik__icontains=search_q)
        )

    profiles = list(qs)

    all_qs = UserProfile.objects
    stats = {
        'total'   : all_qs.count(),
        'pending' : all_qs.filter(status_verifikasi='pending').count(),
        'verified': all_qs.filter(status_verifikasi='verified').count(),
    }

    return render(request, 'account/staff_dashboard.html', {
        'profiles'     : profiles,
        'stats'        : stats,
        'status_filter': status_filter,
        'search_q'     : search_q,
    })


@staff_desa_required
def staff_profile_detail(request, pk):
    profile = get_object_or_404(
        UserProfile.objects.select_related('user'),
        pk=pk,
    )

    if request.method == 'POST':
        new_status   = request.POST.get('status', '').strip()
        catatan      = request.POST.get('catatan', '').strip()

        if new_status in ['pending', 'verified']:
            profile.status_verifikasi = new_status

        profile.catatan_admin = catatan
        profile.save()

        label = 'Diverifikasi' if new_status == 'verified' else 'Dikembalikan ke Pending'
        messages.success(request, f"Profil {profile.user.get_full_name() or profile.user.username} berhasil {label}.")
        return redirect('account_staff:dashboard')

    return render(request, 'account/staff_detail.html', {'profile': profile})