# service/utils/pdf_business_letter.py

import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm

from .pdf_common import (
    draw_kop_surat, draw_judul_surat, draw_pemohon_data,
    draw_wrapped, draw_signature_block, draw_data_table,
    STANDARD_PENUTUP_TEXT,
)


def _format_rupiah(amount: int) -> str:
    return f"Rp {amount:,.0f}".replace(",", ".")


def generate_business_letter_pdf(letter_obj) -> io.BytesIO:
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
    y = draw_judul_surat(p, width, y, "SURAT KETERANGAN USAHA", letter_obj.reference_number)

    pembuka = (
        "Yang bertanda tangan di bawah ini, Kepala Desa Sungai Meriam, Kecamatan Anggana, "
        "Kabupaten Kutai Kartanegara, dengan ini menerangkan bahwa:"
    )
    y = draw_wrapped(p, pembuka, 1.8 * cm, y, width - 3.6 * cm, 10)
    y -= 0.5 * cm

    y = draw_pemohon_data(p, letter_obj.user, profile, 1.8 * cm, y, col_label, col_val)
    y -= 0.5 * cm

    p.setFont("Helvetica-Bold", 10)
    p.drawString(1.8 * cm, y, "DATA USAHA")
    y -= 0.5 * cm

    lama_str = (
        f"{letter_obj.lama_usaha_tahun} tahun"
        if letter_obj.lama_usaha_tahun > 0
        else "Kurang dari 1 tahun"
    )

    y = draw_data_table(p, [
        ("Nama Usaha",     letter_obj.nama_usaha),
        ("Jenis Usaha",    letter_obj.jenis_usaha_display_full),
        ("Alamat Usaha",   letter_obj.alamat_usaha),
        ("Lama Berdiri",   lama_str),
        ("Omset/Bulan",    _format_rupiah(letter_obj.omset_perbulan)),
        ("Keperluan Surat",letter_obj.keperluan_display_full),
        ("Ditujukan Ke",   letter_obj.tujuan_instansi),
    ], 1.8 * cm, y, col_label, col_val)
    y -= 0.7 * cm

    pernyataan = (
        f"Berdasarkan keterangan yang ada, yang bersangkutan tersebut di atas adalah benar-benar "
        f"warga Desa Sungai Meriam yang menjalankan usaha {letter_obj.jenis_usaha_display_full.lower()} "
        f"dengan nama usaha \"{letter_obj.nama_usaha}\" yang beralamat di {letter_obj.alamat_usaha}. "
        f"Surat keterangan ini diterbitkan untuk keperluan {letter_obj.keperluan_display_full.lower()} "
        f"pada {letter_obj.tujuan_instansi}."
    )
    y = draw_wrapped(p, pernyataan, 1.8 * cm, y, width - 3.6 * cm, 10)
    y -= 0.7 * cm

    y = draw_wrapped(p, STANDARD_PENUTUP_TEXT, 1.8 * cm, y, width - 3.6 * cm, 10)
    y -= 1.2 * cm

    draw_signature_block(p, width, y, letter_obj.qr_code, tanggal_str)

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer