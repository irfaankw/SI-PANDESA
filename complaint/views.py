from django.shortcuts import render, redirect

from core.decorators import login_required_custom
from .models import ComplaintReport
from .forms import ComplaintForm

@login_required_custom
def complaint_view(request):
    # Ambil semua aduan user, urutkan terbaru
    complaints = ComplaintReport.objects.filter(user=request.user).order_by('-created_at')
    latest     = complaints.first()

    is_pending_view  = bool(latest and latest.is_pending)

    if request.method == 'POST':
        form = ComplaintForm(request.POST, request.FILES)

        if form.is_valid():
            # Rate limit 5 menit
            if form.check_rate_limit(request.user):
                form.add_error(None, 'Anda baru saja mengirimkan pengaduan. Silakan tunggu 5 menit sebelum mengirim lagi.')
                return render(request, 'complaint/complaint.html', _complaint_ctx(complaints, latest, is_pending_view, form))

            cd = form.cleaned_data
            ComplaintReport.objects.create(
                user          = request.user,
                judul         = cd['judul'],
                kategori      = cd['kategori'],
                kategori_lain = cd.get('kategori_lain', ''),
                lokasi        = cd.get('lokasi', ''),
                deskripsi     = cd['deskripsi'],
                bukti_foto    = cd.get('bukti_foto'),
            )
            return redirect('complaint:complaint_success')

        return render(request, 'complaint/complaint.html', _complaint_ctx(complaints, latest, is_pending_view, form))

    form = ComplaintForm()
    return render(request, 'complaint/complaint.html', _complaint_ctx(complaints, latest, is_pending_view, form))

@login_required_custom
def complaint_success_view(request):
    latest = ComplaintReport.objects.filter(user=request.user).order_by('-created_at').first()
    return render(request, 'complaint/complaint_success.html', {
        'active_tab': 'pengaduan',
        'latest_request': latest,
    })

@login_required_custom  
def complaint_history_view(request):
    complaints = ComplaintReport.objects.filter(user=request.user).order_by('-created_at')
    
    profile     = request.user.profile if hasattr(request.user, 'profile') else None
    is_verified = profile.is_verified if profile else False

    return render(request, 'complaint/complaint_history.html', {
        'active_tab' : 'pengaduan',
        'complaints' : complaints,
        'profile'    : profile,
        'is_verified': is_verified,
    })

def _complaint_ctx(complaints, latest, is_pending_view, form):
    return {
        'active_tab'      : 'pengaduan',
        'complaints'      : complaints,
        'latest_request'  : latest,
        'is_pending_view' : is_pending_view,
        'form'            : form,
    }