import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm

from .pdf_common import (
    draw_kop_surat, draw_judul_surat, draw_pemohon_data,
    draw_wrapped, draw_signature_block, draw_data_table,
    STANDARD_PENUTUP_TEXT,
)


def generate_domicile_letter_pdf(letter_obj) -> io.BytesIO:
    try:
        letter_obj.refresh_from_db(fields=['qr_code', 'approved_at', 'berlaku_hingga'])
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

    tanggal_surat      = letter_obj.approved_at or letter_obj.updated_at
    tanggal_str        = tanggal_surat.strftime('%d %B %Y')
    berlaku_hingga_str = letter_obj.berlaku_hingga.strftime('%d %B %Y') if letter_obj.berlaku_hingga else '-'

    col_label = 5.0 * cm
    col_val   = width - 1.8 * cm - col_label - 0.5 * cm - 1.8 * cm

    y = draw_kop_surat(p, width, height)
    y = draw_judul_surat(p, width, y, "SURAT KETERANGAN DOMISILI", letter_obj.reference_number)

    pembuka = (
        "Yang bertanda tangan di bawah ini, Kepala Desa Sungai Meriam, Kecamatan Anggana, "
        "Kabupaten Kutai Kartanegara, dengan ini menerangkan bahwa orang yang tersebut "
        "namanya di bawah ini benar-benar berdomisili/bertempat tinggal di wilayah "
        "Desa Sungai Meriam:"
    )
    y = draw_wrapped(p, pembuka, 1.8 * cm, y, width - 3.6 * cm, 10)
    y -= 0.5 * cm

    y = draw_pemohon_data(p, letter_obj.user, profile, 1.8 * cm, y, col_label, col_val,
                      alamat_label="Alamat Asal Pemohon")
    y -= 0.5 * cm

    p.setFont("Helvetica-Bold", 10)
    p.drawString(1.8 * cm, y, "DATA DOMISILI")
    y -= 0.5 * cm

    y = draw_data_table(p, [
        ("Status Tempat Tinggal", letter_obj.get_status_tempat_tinggal_display()),
        ("Lama Tinggal",          letter_obj.lama_tinggal_display),
        ("Keperluan",             letter_obj.keperluan),
        ("Ditujukan Kepada",      letter_obj.tujuan_instansi),
        ("Berlaku Hingga",        berlaku_hingga_str),
    ], 1.8 * cm, y, col_label, col_val)
    y -= 0.7 * cm

    masa_berlaku_info = (
        f"Surat keterangan ini berlaku selama {letter_obj.MASA_BERLAKU_BULAN} bulan terhitung "
        f"sejak tanggal diterbitkan, yaitu sampai dengan {berlaku_hingga_str}, dan wajib "
        "diperpanjang apabila digunakan setelah tanggal tersebut."
    )
    y = draw_wrapped(p, masa_berlaku_info, 1.8 * cm, y, width - 3.6 * cm, 10)
    y -= 0.3 * cm

    y = draw_wrapped(p, STANDARD_PENUTUP_TEXT, 1.8 * cm, y, width - 3.6 * cm, 10)
    y -= 1.2 * cm

    draw_signature_block(p, width, y, letter_obj.qr_code, tanggal_str)

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer