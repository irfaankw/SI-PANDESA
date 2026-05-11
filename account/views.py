from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from urllib.parse import urlparse, urlunparse

from .forms import LoginForm, RegisterForm, UserProfileForm, AvatarForm
from .models import UserProfile

# ─────────────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────────────

def _clean_referer(request, modal_tab):
    """
    Ambil HTTP_REFERER, buang query string lama,
    lalu tempel ?auth_modal=<tab> yang bersih.
    """
    referer = request.META.get('HTTP_REFERER', '/')
    parsed  = urlparse(referer)
    clean   = urlunparse(parsed._replace(query='', fragment=''))
    return f"{clean}?auth_modal={modal_tab}"

def _get_or_create_profile(user):
    profile, _ = UserProfile.objects.get_or_create(user=user)
    return profile

# ─────────────────────────────────────────────────────────────
#  AUTH VIEWS
# ─────────────────────────────────────────────────────────────

def login_view(request):
    if request.method != 'POST':
        return redirect('/')
    form     = LoginForm(request.POST)
    next_url = request.POST.get('next', '/')
    if not form.is_valid():
        # Kirim error per field supaya bisa ditampilkan inline di template
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f"login:{field}:{error}")
        return redirect(_clean_referer(request, 'login'))
    email    = form.cleaned_data['email']
    password = form.cleaned_data['password']
    try:
        user_obj = User.objects.get(email=email)
    except User.DoesNotExist:
        messages.error(request, 'login:__all__:Akun dengan email tersebut tidak ditemukan.')
        return redirect(_clean_referer(request, 'login'))
    user = authenticate(request, username=user_obj.username, password=password)
    if user is not None:
        login(request, user)
        _get_or_create_profile(user)          # pastikan profil selalu ada
        # Pesan sambutan — ditampilkan sebagai bubble di beranda
        messages.success(request, f'Selamat datang kembali, {user.first_name or user.username}!')
        parsed_next = urlparse(next_url)
        clean_next  = urlunparse(parsed_next._replace(query='', fragment='')) or '/'
        return redirect(clean_next)
    else:
        messages.error(request, 'login:password:Password yang kamu masukkan salah.')
        return redirect(_clean_referer(request, 'login'))

def register_view(request):
    if request.method != 'POST':
        return redirect('/')
    form = RegisterForm(request.POST)
    if not form.is_valid():
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f"register:{field}:{error}")
        return redirect(_clean_referer(request, 'register'))
    email    = form.cleaned_data['email']
    nama     = form.cleaned_data['nama_lengkap']
    no_hp    = form.cleaned_data['no_hp']
    password = form.cleaned_data['password']
    if User.objects.filter(email=email).exists():
        messages.error(request, 'register:email:Email sudah terdaftar. Silakan masuk.')
        return redirect(_clean_referer(request, 'register'))
    nama_parts = nama.strip().split(' ', 1)
    first_name = nama_parts[0]
    last_name  = nama_parts[1] if len(nama_parts) > 1 else ''
    user = User.objects.create_user(
        username=email,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
    )
    # Buat profil sekaligus simpan no_hp awal
    profile       = _get_or_create_profile(user)
    profile.no_hp = no_hp
    profile.save()
    login(request, user)
    messages.success(request, f'Selamat datang, {first_name}! Akun berhasil dibuat.')
    return redirect('core:index')

def logout_view(request):
    logout(request)
    return redirect('core:index')

# ─────────────────────────────────────────────────────────────
#  PROFILE VIEW
# ─────────────────────────────────────────────────────────────

@login_required(login_url='/?auth_modal=login')
def profile_view(request):
    profile     = _get_or_create_profile(request.user)
    is_verified = profile.is_verified
    if request.method == 'POST':
        action = request.POST.get('action', 'biodata')
        # ── Upload Avatar ──────────────────────────────────
        if action == 'avatar':
            avatar_form = AvatarForm(request.POST, request.FILES, instance=profile)
            if avatar_form.is_valid():
                avatar_form.save()
                messages.success(request, 'Foto profil berhasil diperbarui.')
            else:
                messages.error(request, 'Gagal mengunggah foto. Pastikan format file valid (JPG/PNG).')
            return redirect('account:profile')
        # ── Update Biodata ─────────────────────────────────
        profile_form = UserProfileForm(
            request.POST,
            request.FILES,
            instance=profile,
            is_verified=is_verified,
        )
        # Nama lengkap — disimpan di User, bukan UserProfile
        nama = request.POST.get('nama_lengkap', '').strip()
        if profile_form.is_valid():
            profile_form.save()
            if nama:
                nama_parts              = nama.split(' ', 1)
                request.user.first_name = nama_parts[0]
                request.user.last_name  = nama_parts[1] if len(nama_parts) > 1 else ''
                request.user.save()
            messages.success(request, 'Data profil berhasil disimpan.')
            return redirect('account:profile')
        else:
            # Kirim error ke template agar bisa ditampilkan inline
            for field, errors in profile_form.errors.items():
                for error in errors:
                    messages.error(request, f"profile:{field}:{error}")
            return redirect('account:profile')

    # ── GET ────────────────────────────────────────────────
    profile_form = UserProfileForm(instance=profile, is_verified=is_verified)
    avatar_form  = AvatarForm(instance=profile)

    # Cek apakah profil belum lengkap (untuk notifikasi)
    profile_incomplete = not all([
        profile.nik, profile.alamat, profile.rt, profile.rw
    ])

    context = {
        'title':              'Profil Pengguna',
        'profile':            profile,
        'profile_form':       profile_form,
        'avatar_form':        avatar_form,
        'profile_incomplete': profile_incomplete,
        'is_verified':        is_verified,
    }
    return render(request, 'account/user_profile.html', context)