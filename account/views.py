from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import User

from .models import UserProfile, EmailOTP
from .forms import UserProfileForm, AvatarForm, EmailOTPRequestForm, EmailOTPVerifyForm

from .forms import UserProfileForm, AvatarForm
from .models import UserProfile

def _get_or_create_profile(user):
    if user.is_staff or user.is_superuser:
        return None
    profile, _ = UserProfile.objects.get_or_create(user=user)
    return profile

def logout_view(request):
    logout(request)
    return redirect('core:index')

@login_required
def profile_view(request):
    if request.user.is_staff or request.user.is_superuser:
        messages.info(request, "Anda login sebagai Admin.")
        return redirect('/admin/')

    profile = _get_or_create_profile(request.user)
    if not profile:
        return redirect('core:index')

    is_verified = profile.is_verified

    if request.method == 'POST':
        action = request.POST.get('action', 'biodata')

        if action == 'avatar':
            avatar_form = AvatarForm(request.POST, request.FILES, instance=profile)
            if avatar_form.is_valid():
                avatar_form.save()
                messages.success(request, 'Foto profil berhasil diperbarui.')
            else:
                messages.error(request, 'Gagal mengunggah foto.')
            return redirect('account:profile')

        profile_form = UserProfileForm(
            request.POST, request.FILES,
            instance=profile,
            is_verified=is_verified,
        )
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
            for field, errors in profile_form.errors.items():
                for error in errors:
                    messages.error(request, f"profile:{field}:{error}")
            return redirect('account:profile')

    profile_form = UserProfileForm(instance=profile, is_verified=is_verified)
    avatar_form  = AvatarForm(instance=profile)

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

def otp_request_view(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Metode tidak diizinkan.'}, status=405)

    form = EmailOTPRequestForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'success': False, 'error': 'Format email tidak valid.'}, status=400)

    email = form.cleaned_data['email'].strip().lower()

    can_resend, wait_seconds = EmailOTP.can_resend(email)
    if not can_resend:
        return JsonResponse({
            'success': False,
            'error': f'Tunggu {wait_seconds} detik sebelum mengirim ulang.',
        }, status=429)

    otp = EmailOTP.generate(email)

    send_mail(
        subject='Kode verifikasi SI-PANDESA',
        message=(
            f'Kode verifikasi kamu: {otp.code}\n\n'
            f'Kode ini berlaku {EmailOTP.EXPIRY_MINUTES} menit. '
            'Jangan bagikan ke siapa pun.'
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )

    request.session['otp_email'] = email
    return JsonResponse({'success': True, 'email': email})


def otp_verify_view(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Metode tidak diizinkan.'}, status=405)

    email = request.session.get('otp_email')
    if not email:
        return JsonResponse({'success': False, 'error': 'Sesi kedaluwarsa, masukkan email lagi.'}, status=400)

    form = EmailOTPVerifyForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'success': False, 'error': 'Kode harus 6 digit angka.'}, status=400)

    code = form.cleaned_data['code']
    otp  = EmailOTP.objects.filter(email=email, is_used=False).order_by('-created_at').first()

    if not otp or otp.is_expired:
        return JsonResponse({'success': False, 'error': 'Kode sudah kedaluwarsa, kirim ulang.'}, status=400)

    if otp.attempts >= EmailOTP.MAX_ATTEMPTS:
        return JsonResponse({'success': False, 'error': 'Terlalu banyak percobaan, kirim ulang kode.'}, status=429)

    if otp.code != code:
        otp.attempts += 1
        otp.save(update_fields=['attempts'])
        sisa = EmailOTP.MAX_ATTEMPTS - otp.attempts
        return JsonResponse({'success': False, 'error': f'Kode salah, sisa {sisa} percobaan.'}, status=400)

    otp.is_used = True
    otp.save(update_fields=['is_used'])

    user = User.objects.filter(email__iexact=email).first()
    if not user:
        username, base, suffix = email.split('@')[0][:150], email.split('@')[0][:150], 1
        while User.objects.filter(username=username).exists():
            username = f"{base}{suffix}"[:150]
            suffix += 1
        user = User.objects.create(email=email, username=username)
        user.set_unusable_password()
        user.save()

    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
    del request.session['otp_email']
    return JsonResponse({'success': True, 'redirect': '/'})