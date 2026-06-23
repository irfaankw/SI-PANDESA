# Kumpulan decorator akses kontrol untuk SI-PANDESA.
# Import dari sini di semua app agar tidak ada duplikasi kode.

from functools import wraps
from django.http import HttpResponseForbidden
from django.shortcuts import redirect

def staff_desa_required(view_func):
    """
    Hanya akun is_staff=True DAN group 'Staff Desa' yang boleh masuk.
    - Belum login       → redirect ke halaman login
    - Login tapi bukan Staff Desa → 403 Forbidden
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.conf import settings
            return redirect(f"{settings.LOGIN_URL}?next={request.path}")

        is_staff_desa = (
            request.user.is_staff
            and request.user.groups.filter(name='Staff Desa').exists()
        )
        if not is_staff_desa:
            return HttpResponseForbidden("""
                <h1 style="font-family:sans-serif">403 – Akses Ditolak</h1>
                <p style="font-family:sans-serif">
                    Halaman ini hanya untuk <strong>Staff Desa</strong>.<br>
                    Pastikan akun sudah ditambahkan ke group
                    <strong>Staff Desa</strong> di halaman Admin Django.
                </p>
            """)
        return view_func(request, *args, **kwargs)
    return wrapper

def nakes_required(view_func):
    """
    Hanya akun group 'Nakes' yang boleh masuk.
    Dipakai di health/views.py menggantikan _is_nakes + user_passes_test.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.conf import settings
            return redirect(f"{settings.LOGIN_URL}?next={request.path}")

        is_nakes = (
            request.user.is_staff
            and request.user.groups.filter(name='Nakes').exists()
        )
        if not is_nakes:
            return HttpResponseForbidden("""
                <h1 style="font-family:sans-serif">403 – Akses Ditolak</h1>
                <p style="font-family:sans-serif">
                    Halaman ini hanya untuk <strong>Tenaga Kesehatan (Nakes)</strong>.
                </p>
            """)
        return view_func(request, *args, **kwargs)
    return wrapper