"""
Generator PDF — Surat Pengantar
Menggunakan helper bersama dari pdf_common.py
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


def generate_intro_letter_pdf(letter_obj) -> io.BytesIO:
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

    y = draw_kop_surat(p, width, height)
    y = draw_judul_surat(p, width, y, "SURAT PENGANTAR", letter_obj.reference_number)

    pembuka = (
        "Yang bertanda tangan di bawah ini, Kepala Desa Sungai Meriam, Kecamatan Anggana, "
        "Kabupaten Kutai Kartanegara, dengan ini menerangkan dan memberikan pengantar kepada:"
    )
    y = draw_wrapped(p, pembuka, 1.8 * cm, y, width - 3.6 * cm, 10)
    y -= 0.5 * cm

    y = draw_pemohon_data(p, letter_obj.user, profile, 1.8 * cm, y, col_label, col_val)
    y -= 0.5 * cm

    p.setFont("Helvetica-Bold", 10)
    p.drawString(1.8 * cm, y, "KEPERLUAN SURAT")
    y -= 0.5 * cm

    keperluan_text = letter_obj.keperluan_display_full
    rows = [
        ("Keperluan",       keperluan_text),
        ("Ditujukan Kepada", letter_obj.tujuan_instansi),
    ]
    if letter_obj.keterangan_tambahan:
        rows.append(("Keterangan", letter_obj.keterangan_tambahan))

    y = draw_data_table(p, rows, 1.8 * cm, y, col_label, col_val)
    y -= 0.7 * cm

    penutup = (
        "Demikian surat pengantar ini dibuat untuk dapat dipergunakan sebagaimana mestinya. "
        "Kepada pihak yang berkepentingan dimohon untuk dapat memberikan bantuan seperlunya "
        "dan atas perhatiannya kami ucapkan terima kasih."
    )
    y = draw_wrapped(p, penutup, 1.8 * cm, y, width - 3.6 * cm, 10)
    y -= 1.2 * cm

    draw_signature_block(p, width, y, letter_obj.qr_code, tanggal_str)

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer