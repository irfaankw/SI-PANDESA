from django.shortcuts import redirect, render
 
def redirect_to_mail(request):
    """Redirect /layanan/ → /layanan/surat/"""
    return redirect('service:surat_digital')
 
def digital_mail_index(request):
    """Halaman tab Surat Digital — menampilkan 7 jenis surat."""
    context = {
        'title':        'Surat Digital | Layanan Desa Sungai Meriam',
        'current_view': 'service:digital_mail',
        'active_tab':   'surat',
    }
    return render(request, 'service/digital_mail.html', context)