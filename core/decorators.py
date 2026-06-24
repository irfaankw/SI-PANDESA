# Kumpulan decorator akses kontrol untuk SI-PANDESA.
# Import dari sini di semua app agar tidak ada duplikasi kode.

from functools import wraps
from urllib.parse import urlparse, urlencode, parse_qs, urlunparse
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


def verified_required(service_name=None):
    """
    Decorator factory: hanya warga berstatus 'verified' yang boleh akses.

    Pemakaian dengan nama layanan eksplisit (dianjurkan):
        @verified_required("Layanan Surat Digital")
        def my_view(request): ...

    Pemakaian tanpa argumen (nama layanan diambil otomatis dari URL):
        @verified_required()
        def my_view(request): ...

    Alur redirect:
        - Belum login  → LOGIN_URL?next=...
        - Pending/none → <current_url>?blocked=1&service=<nama>
                         (jika sudah ada ?blocked → redirect ke /?blocked=1&service=<nama>
                          untuk hindari loop)
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # 1. Wajib login
            if not request.user.is_authenticated:
                from django.conf import settings
                return redirect(f"{settings.LOGIN_URL}?next={request.path}")

            # 2. Cek status verifikasi
            try:
                profile = request.user.profile
                is_verified = (profile.status_verifikasi == 'verified')
            except Exception:
                is_verified = False

            if not is_verified:
                # Tentukan nama layanan untuk ditampilkan di pop-up
                _service = service_name or _guess_service_name(request.path)

                # Redirect ke halaman saat ini + parameter blocked & service
                current_url = request.path
                parsed = urlparse(request.get_full_path())

                if 'blocked' in parsed.query:
                    # Sudah ada ?blocked → hindari loop, arahkan ke home
                    return redirect(f"/?blocked=1&service={_service}")

                sep = '&' if parsed.query else '?'
                return redirect(
                    f"{current_url}?blocked=1&service={_service}"
                )

            return view_func(request, *args, **kwargs)
        return wrapper

    # Dukung pemakaian @verified_required (tanpa kurung) maupun @verified_required()
    if callable(service_name):
        # Dipanggil sebagai @verified_required tanpa argumen
        _fn = service_name
        service_name = None
        return decorator(_fn)

    return decorator


def _guess_service_name(path):
    """Tebak nama layanan berdasarkan URL path (fallback)."""
    path = path.lower()
    if 'welfare' in path or 'kesejahteraan' in path or 'bansos' in path:
        return 'Layanan Kesejahteraan'
    if 'service' in path or 'surat' in path or 'layanan' in path:
        return 'Layanan Surat Digital'
    return 'Layanan ini'


def login_required_custom(view_func):
    """
    Hanya perlu login — pending maupun verified boleh akses.
    Untuk: pengaduan, kesehatan.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.conf import settings
            return redirect(f"{settings.LOGIN_URL}?next={request.path}")
        return view_func(request, *args, **kwargs)
    return wrapper