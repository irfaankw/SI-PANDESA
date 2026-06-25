from django.shortcuts import render
from service.models import (
    MoveLetterRequest, DomicileLetterRequest, DeathLetterRequest,
    BirthLetterRequest, PovertyLetterRequest, BusinessLetterRequest,
    IntroLetterRequest,
)
from complaint.models import ComplaintReport
from health.models import AntreanKesehatan
from welfare.models import UMKM, PengajuanBansos


LETTER_MAP = [
    (MoveLetterRequest,     'Surat Keterangan Pindah'),
    (DomicileLetterRequest, 'Surat Keterangan Domisili'),
    (DeathLetterRequest,    'Surat Keterangan Kematian'),
    (BirthLetterRequest,    'Surat Keterangan Kelahiran'),
    (PovertyLetterRequest,  'Surat Keterangan Tidak Mampu'),
    (BusinessLetterRequest, 'Surat Keterangan Usaha'),
    (IntroLetterRequest,    'Surat Pengantar'),
]


def lacak_view(request):
    q     = request.GET.get('q', '').strip().upper()
    hasil = None
    tipe  = None
    error = None

    if q:
        # ── 1. Cari Surat Digital (PKU-XXXX-XXXXXX) ──
        for model, label in LETTER_MAP:
            try:
                obj   = model.objects.select_related('user').get(reference_number=q)
                hasil = obj
                tipe  = {'label': label, 'jenis': 'surat'}
                break
            except model.DoesNotExist:
                continue

        # ── 2. Cari Pengaduan (ADU-XXXX-XXXXXX) ──
        if not hasil:
            try:
                obj   = ComplaintReport.objects.select_related('user').get(reference_number=q)
                hasil = obj
                tipe  = {'label': 'Laporan Pengaduan', 'jenis': 'pengaduan'}
            except ComplaintReport.DoesNotExist:
                pass

        # ── 3. Cari Antrean Kesehatan (by kode_unik UUID) ──
        if not hasil:
            try:
                import uuid
                kode = uuid.UUID(q.lower())
                obj  = AntreanKesehatan.objects.select_related('user').get(kode_unik=kode)
                hasil = obj
                tipe  = {'label': 'Antrean Kesehatan', 'jenis': 'kesehatan'}
            except (ValueError, AntreanKesehatan.DoesNotExist):
                pass

        # ── 4. Cari UMKM (UMKM-XXXXXX-XXXX) ──
        if not hasil:
            try:
                obj   = UMKM.objects.select_related('pemilik').get(nomor_pengajuan=q)
                hasil = obj
                tipe  = {'label': 'Pendaftaran UMKM', 'jenis': 'umkm'}
            except UMKM.DoesNotExist:
                pass

        # ── 5. Cari Bansos (by ID angka) ──
        if not hasil and q.isdigit():
            try:
                obj   = PengajuanBansos.objects.select_related(
                    'user', 'program'
                ).get(id=int(q))
                hasil = obj
                tipe  = {'label': 'Pengajuan Bansos', 'jenis': 'bansos'}
            except PengajuanBansos.DoesNotExist:
                pass

        if not hasil:
            error = f'Nomor pengajuan "{q}" tidak ditemukan.'

    return render(request, 'core/lacak_pengajuan.html', {
    'q'    : q,
    'hasil': hasil,
    'tipe' : tipe,
    'error': error,
    'panduan': [
        {'label': 'Surat Digital', 'contoh': 'PKU-2026-XXXXXX'},
        {'label': 'Pengaduan',     'contoh': 'ADU-2026-XXXXXX'},
        {'label': 'Kesehatan',     'contoh': 'UUID (dari tiket antrean)'},
        {'label': 'UMKM',          'contoh': 'UMKM-202606-XXXX'},
        {'label': 'Bansos',        'contoh': 'ID angka (dari riwayat)'},
    ],
})