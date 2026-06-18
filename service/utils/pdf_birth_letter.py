"""
Generator PDF Surat Keterangan Kelahiran.
Menggunakan semua helper dari pdf_common.py.
"""

import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm

from .pdf_common import (
    draw_kop_surat, draw_judul_surat, draw_pemohon_data,
    draw_wrapped, draw_signature_block, draw_data_table,
    STANDARD_PENUTUP_TEXT,
)

BULAN_ID = {
    1: 'Januari', 2: 'Februari', 3: 'Maret', 4: 'April',
    5: 'Mei', 6: 'Juni', 7: 'Juli', 8: 'Agustus',
    9: 'September', 10: 'Oktober', 11: 'November', 12: 'Desember',
}


def _fmt_date(d):
    """Format date object ke '01 Januari 2024'."""
    if not d:
        return '-'
    return f"{d.day:02d} {BULAN_ID.get(d.month, '')} {d.year}"


def generate_birth_letter_pdf(letter_obj) -> io.BytesIO:
    try:
        letter_obj.refresh_from_db(fields=['qr_code', 'approved_at'])
    except Exception:
        pass

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    profile = None
    try:
        profile = letter_obj.user.profile
    except Exception:
        pass

    tanggal_surat = letter_obj.approved_at or letter_obj.updated_at
    tanggal_str   = tanggal_surat.strftime('%d %B %Y')

    col_label = 5.0 * cm
    col_val   = width - 1.8 * cm - col_label - 0.5 * cm - 1.8 * cm

    # ── Kop & Judul ───────────────────────────────────────────
    y = draw_kop_surat(p, width, height)
    y = draw_judul_surat(
        p, width, y,
        "SURAT KETERANGAN KELAHIRAN",
        letter_obj.reference_number,
    )

    # ── Pembuka ───────────────────────────────────────────────
    pembuka = (
        "Yang bertanda tangan di bawah ini, Kepala Desa Sungai Meriam, Kecamatan Anggana, "
        "Kabupaten Kutai Kartanegara, dengan ini menerangkan bahwa telah lahir seorang bayi "
        "dengan keterangan sebagai berikut:"
    )
    y = draw_wrapped(p, pembuka, 1.8 * cm, y, width - 3.6 * cm, 10)
    y -= 0.5 * cm

    # ── Data Bayi ─────────────────────────────────────────────
    p.setFont("Helvetica-Bold", 10)
    p.drawString(1.8 * cm, y, "DATA BAYI")
    y -= 0.5 * cm

    jk_display = 'Laki-laki' if letter_obj.jenis_kelamin_bayi == 'L' else 'Perempuan'
    y = draw_data_table(p, [
        ("Nama Bayi",       letter_obj.nama_bayi),
        ("Jenis Kelamin",   jk_display),
        ("Tempat Lahir",    letter_obj.tempat_lahir_bayi),
        ("Tanggal Lahir",   _fmt_date(letter_obj.tanggal_lahir_bayi)),
        ("Anak Ke-",        str(letter_obj.anak_ke)),
    ], 1.8 * cm, y, col_label, col_val)
    y -= 0.7 * cm

    # ── Data Orang Tua ────────────────────────────────────────
    p.setFont("Helvetica-Bold", 10)
    p.drawString(1.8 * cm, y, "DATA ORANG TUA")
    y -= 0.5 * cm

    y = draw_data_table(p, [
        ("Nama Ayah",  letter_obj.nama_ayah),
        ("NIK Ayah",   letter_obj.nik_ayah),
        ("Nama Ibu",   letter_obj.nama_ibu),
        ("NIK Ibu",    letter_obj.nik_ibu),
    ], 1.8 * cm, y, col_label, col_val)
    y -= 0.7 * cm

    # ── Data Pelapor (dari profil user) ──────────────────────
    p.setFont("Helvetica-Bold", 10)
    p.drawString(1.8 * cm, y, "DATA PELAPOR")
    y -= 0.5 * cm

    y = draw_pemohon_data(
        p, letter_obj.user, profile,
        1.8 * cm, y, col_label, col_val,
        alamat_label="Alamat",
    )
    y -= 0.7 * cm

    # ── Penutup ───────────────────────────────────────────────
    y = draw_wrapped(p, STANDARD_PENUTUP_TEXT, 1.8 * cm, y, width - 3.6 * cm, 10)
    y -= 1.2 * cm

    # ── Tanda Tangan + QR ─────────────────────────────────────
    draw_signature_block(p, width, y, letter_obj.qr_code, tanggal_str)

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer