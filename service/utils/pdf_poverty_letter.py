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
    """Format angka ke format rupiah: Rp 1.500.000"""
    return f"Rp {amount:,.0f}".replace(",", ".")


def generate_poverty_letter_pdf(letter_obj) -> io.BytesIO:
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
    y = draw_judul_surat(p, width, y, "SURAT KETERANGAN TIDAK MAMPU", letter_obj.reference_number)

    pembuka = (
        "Yang bertanda tangan di bawah ini, Kepala Desa Sungai Meriam, Kecamatan Anggana, "
        "Kabupaten Kutai Kartanegara, dengan ini menerangkan dengan sesungguhnya bahwa:"
    )
    y = draw_wrapped(p, pembuka, 1.8 * cm, y, width - 3.6 * cm, 10)
    y -= 0.5 * cm

    y = draw_pemohon_data(p, letter_obj.user, profile, 1.8 * cm, y, col_label, col_val)
    y -= 0.5 * cm

    p.setFont("Helvetica-Bold", 10)
    p.drawString(1.8 * cm, y, "KETERANGAN EKONOMI")
    y -= 0.5 * cm

    keperluan_text = letter_obj.keperluan_display_full
    tanggungan_str = (
        f"{letter_obj.jumlah_tanggungan} orang"
        if letter_obj.jumlah_tanggungan > 0
        else "Tidak ada tanggungan"
    )

    y = draw_data_table(p, [
        ("Keperluan Surat",   keperluan_text),
        ("Ditujukan Kepada",  letter_obj.tujuan_instansi),
        ("Penghasilan/Bulan", _format_rupiah(letter_obj.penghasilan)),
        ("Jumlah Tanggungan", tanggungan_str),
    ], 1.8 * cm, y, col_label, col_val)
    y -= 0.7 * cm

    pernyataan = (
        f"Berdasarkan data yang ada dan kenyataan yang sebenarnya, yang bersangkutan "
        f"tersebut di atas adalah benar-benar termasuk warga yang TIDAK MAMPU / kurang "
        f"mampu secara ekonomi yang berdomisili di wilayah Desa Sungai Meriam. "
        f"Surat keterangan ini dibuat untuk keperluan {keperluan_text.lower()} "
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