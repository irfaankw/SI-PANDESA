import io
import base64
import qrcode

from datetime import datetime, timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.contrib import messages

from .models import AntreanKesehatan


# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────

POLI_CHOICES = [
    ('umum',   'Poli Umum'),
    ('gigi',   'Poli Gigi'),
    ('kia',    'KIA / Kebidanan'),
    ('lansia', 'Poli Lansia'),
    ('gizi',   'Poli Gizi'),
]

JAM_BUKA_ESTIMASI  = 8   # 08:00 WITA
DURASI_MENIT       = 15  # menit per pasien
JAM_CUTOFF_EXPIRED = 14  # 14:00 WITA — antrean hangus setelah jam ini


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _is_nakes(user):
    return user.is_authenticated and (
        user.groups.filter(name='Nakes').exists() or user.is_staff
    )


def _get_next_queue_number(poli: str, date) -> int:
    last = (
        AntreanKesehatan.objects
        .filter(poli=poli, tanggal_kunjungan=date)
        .order_by('-nomor_antrean')
        .first()
    )
    return (last.nomor_antrean + 1) if last else 1


def _calculate_schedule(queue_number: int, date):
    base  = datetime(date.year, date.month, date.day, JAM_BUKA_ESTIMASI, 0)
    start = base + timedelta(minutes=(queue_number - 1) * DURASI_MENIT)
    end   = start + timedelta(minutes=DURASI_MENIT)
    return start.time(), end.time()


def _make_qr_base64(data: str) -> str:
    qr = qrcode.QRCode(version=1, box_size=6, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    img    = qr.make_image(fill_color='black', back_color='white')
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode('utf-8')


def _get_target_date(today):
    """Hitung tanggal kunjungan valid berikutnya (H+1, skip Minggu)."""
    target = today + timedelta(days=1)
    while target.weekday() == 6:  # skip Minggu
        target += timedelta(days=1)
    return target


def _check_expired_queues(user, today):
    """Lazy expiry — menghanguskan antrean hari ini jika lewat 14:00 WITA."""
    now_local = timezone.localtime(timezone.now())

    if now_local.hour < JAM_CUTOFF_EXPIRED:
        return

    AntreanKesehatan.objects.filter(
        user              = user,
        status            = 'menunggu',
        tanggal_kunjungan = today,
    ).update(status='expired')


def _get_active_queue(user, today, target_date):
    """Ambil antrean aktif user hari ini maupun besok."""
    return (
        AntreanKesehatan.objects
        .filter(
            user                    = user,
            status__in              = ['menunggu', 'hadir'],
            tanggal_kunjungan__in   = [today, target_date],
        )
        .order_by('tanggal_kunjungan', 'nomor_antrean')
        .first()
    )


# ─────────────────────────────────────────────────────────────────────────────
# USER VIEWS
# ─────────────────────────────────────────────────────────────────────────────

@login_required
def appointment_view(request):
    profile     = getattr(request.user, 'profile', None)
    today       = timezone.localdate()
    target_date = _get_target_date(today)

    # ── STEP 1: Lazy expire antrean HARI INI ──
    _check_expired_queues(request.user, today)

    # ── STEP 2: Query state antrean user ──
    active_queue = _get_active_queue(request.user, today, target_date)

    today_completed_queue = (
        AntreanKesehatan.objects
        .filter(user=request.user, status='selesai', tanggal_kunjungan=today)
        .first()
    )

    today_expired_queue = (
        AntreanKesehatan.objects
        .filter(user=request.user, status='expired', tanggal_kunjungan=today)
        .first()
    )

    # ── STEP 3: Handle POST ───────────────────────────────────────────
    if request.method == 'POST':

        # Langsung tolak request jika user terdeteksi sudah memiliki antrean aktif atau rekam hari ini
        if active_queue or today_completed_queue or today_expired_queue:
            return JsonResponse({'status': 'error', 'message': 'Akses ditolak.'}, status=400)

        # ── Ambil input form ──────────────────────────────────────────
        nama_pasien = request.POST.get('nama_pasien', '').strip()
        nik         = request.POST.get('nik', '').strip()
        no_hp       = request.POST.get('no_hp', '').strip()
        no_bpjs     = request.POST.get('no_bpjs', '').strip()
        keluhan     = request.POST.get('keluhan', '').strip()
        poli        = request.POST.get('poli', '').strip()
        tgl_str     = request.POST.get('tanggal_kunjungan', '').strip()

        errors = {}
        if not nama_pasien:
            errors['nama_pasien'] = 'Nama pasien wajib diisi.'
        if not nik or len(nik) != 16 or not nik.isdigit():
            errors['nik'] = 'NIK harus 16 digit angka.'
        if not no_hp:
            errors['no_hp'] = 'Nomor telepon wajib diisi.'
        if not keluhan:
            errors['keluhan'] = 'Keluhan / gejala wajib diisi.'
        if not poli or poli not in dict(POLI_CHOICES):
            errors['poli'] = 'Pilih poli yang tersedia.'
        if not tgl_str:
            errors['tanggal_kunjungan'] = 'Tanggal kunjungan wajib diisi.'

        visit_date = None
        if tgl_str and 'tanggal_kunjungan' not in errors:
            try:
                visit_date = datetime.strptime(tgl_str, '%Y-%m-%d').date()

                if visit_date != target_date:
                    errors['tanggal_kunjungan'] = 'Pendaftaran hanya untuk kunjungan besok.'
                elif visit_date.weekday() == 6:
                    errors['tanggal_kunjungan'] = 'Puskesmas tutup setiap hari Minggu.'

            except ValueError:
                errors['tanggal_kunjungan'] = 'Format tanggal tidak valid.'

        if errors:
            return JsonResponse({'status': 'error', 'errors': errors}, status=400)

        # ── Buat antrean baru ─────────────────────────────────────────
        queue_number         = _get_next_queue_number(poli, visit_date)
        time_start, time_end = _calculate_schedule(queue_number, visit_date)

        queue = AntreanKesehatan.objects.create(
            user              = request.user,
            nama_pasien       = nama_pasien,
            nik               = nik,
            no_hp             = no_hp,
            no_bpjs           = no_bpjs or None,
            keluhan           = keluhan,
            poli              = poli,
            tanggal_kunjungan = visit_date,
            nomor_antrean     = queue_number,
            estimasi_mulai    = time_start,
            estimasi_selesai  = time_end,
            status            = 'menunggu',
        )

        checkin_url = request.build_absolute_uri(
            f'/layanan/kesehatan/checkin/{queue.kode_unik}/'
        )
        qr_base64  = _make_qr_base64(checkin_url)
        poli_label = dict(POLI_CHOICES).get(poli, poli)

        return JsonResponse({
            'status': 'success',
            'data': {
                'nomor_antrean':   queue.nomor_antrean_display,
                'nama_pasien':     nama_pasien,
                'poli':            poli_label,
                'tanggal_display': visit_date.strftime('%d %B %Y'),
                'estimasi': (
                    f'{time_start.strftime("%H.%M")} – '
                    f'{time_end.strftime("%H.%M")} WITA'
                ),
                'lokasi':    'Puskesmas Desa Sungai Meriam',
                'qr_base64': qr_base64,
                'kode_unik': str(queue.kode_unik),
            }
        })

    # ── STEP 4: GET — siapkan context ────────────────────────────────
    active_queue_qr = None
    if active_queue:
        checkin_url = request.build_absolute_uri(
            f'/layanan/kesehatan/checkin/{active_queue.kode_unik}/'
        )
        active_queue_qr = _make_qr_base64(checkin_url)

    context = {
        'title':                  'Layanan Kesehatan | Desa Sungai Meriam',
        'current_view':           'health:appointment',
        'active_tab':             'kesehatan',
        'poli_choices':           POLI_CHOICES,
        'profile':                profile,
        'min_date':               target_date.strftime('%Y-%m-%d'),
        'max_date':               target_date.strftime('%Y-%m-%d'),
        'default_date':           target_date.strftime('%Y-%m-%d'),
        'active_queue':           active_queue,
        'active_queue_qr':        active_queue_qr,
        'today_completed_queue':  today_completed_queue,
        'today_expired_queue':    today_expired_queue,
        'prefill_nama':           request.user.get_full_name() or request.user.username,
        'prefill_nik':            profile.nik if profile else '',
        'prefill_no_hp':          profile.no_hp if profile else '',
    }
    return render(request, 'health/appointment.html', context)


@login_required
def medical_history_view(request):
    profile = getattr(request.user, 'profile', None)

    completed_visits = (
        AntreanKesehatan.objects
        .filter(user=request.user, status='selesai')
        .order_by('-tanggal_kunjungan')
        .select_related('ditangani_oleh')
    )

    is_verified        = (profile.status_verifikasi == 'verified') if profile else False
    profile_incomplete = bool(
        profile and not all([profile.nik, profile.alamat, profile.rt])
    )

    context = {
        'title':              'Riwayat Berobat | Desa Sungai Meriam',
        'current_view':       'health:medical_history',
        'active_tab':         'kesehatan',
        'profile':            profile,
        'completed_visits':   completed_visits,
        'is_verified':        is_verified,
        'profile_incomplete': profile_incomplete,
    }
    return render(request, 'health/medical_history.html', context)


def qr_checkin_view(request, kode):
    queue = get_object_or_404(AntreanKesehatan, kode_unik=kode)
    context = {
        'title':    'Verifikasi Antrean',
        'queue':    queue,
        'is_nakes': _is_nakes(request.user) if request.user.is_authenticated else False,
    }
    return render(request, 'health/qr_verification.html', context)


@login_required
@user_passes_test(_is_nakes, login_url='/')
@require_POST
def confirm_attendance_view(request, pk):
    queue = get_object_or_404(AntreanKesehatan, pk=pk)
    if queue.status == 'menunggu':
        queue.status = 'hadir'
        queue.save(update_fields=['status', 'updated_at'])
        messages.success(request, f'Kehadiran {queue.nama_pasien} berhasil dikonfirmasi.')
    return redirect('health:qr_checkin', kode=queue.kode_unik)


# ─────────────────────────────────────────────────────────────────────────────
# NAKES VIEWS
# ─────────────────────────────────────────────────────────────────────────────

@login_required
@user_passes_test(_is_nakes, login_url='/')
def medical_dashboard_view(request):
    today       = timezone.localdate()
    poli_filter = request.GET.get('poli', '')
    date_filter = request.GET.get('tanggal', str(today))

    try:
        filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
    except ValueError:
        filter_date = today

    queues = AntreanKesehatan.objects.filter(
        tanggal_kunjungan=filter_date
    ).select_related('user')

    if poli_filter:
        queues = queues.filter(poli=poli_filter)

    queues = queues.order_by('nomor_antrean')

    context = {
        'title':        'Dashboard Nakes | Puskesmas Sungai Meriam',
        'queues':       queues,
        'poli_choices': POLI_CHOICES,
        'poli_filter':  poli_filter,
        'filter_date':  filter_date,
        'today':        today,
    }
    return render(request, 'health/medical_dashboard.html', context)


@login_required
@user_passes_test(_is_nakes, login_url='/')
@require_POST
def medical_input_view(request, pk):
    queue = get_object_or_404(AntreanKesehatan, pk=pk)

    diagnosa      = request.POST.get('diagnosa', '').strip()
    resep_obat    = request.POST.get('resep_obat', '').strip()
    catatan_nakes = request.POST.get('catatan_nakes', '').strip()

    if not diagnosa:
        messages.error(request, 'Diagnosa wajib diisi.')
        return redirect('health:medical_dashboard')

    queue.diagnosa       = diagnosa
    queue.resep_obat     = resep_obat or None
    queue.catatan_nakes  = catatan_nakes or None
    queue.status         = 'selesai'
    queue.ditangani_oleh = request.user
    queue.waktu_selesai  = timezone.now()
    queue.save()

    messages.success(request, f'Data pasien {queue.nama_pasien} berhasil disimpan.')
    return redirect('health:medical_dashboard')