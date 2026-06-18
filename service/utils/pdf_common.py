"""
Helper bersama untuk seluruh generator PDF surat digital.
Menangani bagian yang SAMA di semua surat: kop surat, judul, data
pemohon, blok tanda tangan + QR, dan utilitas menggambar teks/tabel.
Tiap pdf_<jenis_surat>.py hanya perlu mengisi bagian ISI yang spesifik.
"""

import io
import os
import urllib.request

from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader


NAMA_DESA         = "Sungai Meriam"
KEPALA_DESA_NAME  = "Muhammad Irfan"

STANDARD_PENUTUP_TEXT = (
    "Demikian surat keterangan ini dibuat dengan sebenarnya dan kepada pihak yang "
    "berkepentingan agar menjadi maklum, atas perhatiannya kami ucapkan terima kasih."
)


def get_logo_path():
    from django.conf import settings
    for static_dir in getattr(settings, 'STATICFILES_DIRS', []):
        path = os.path.join(static_dir, 'assets', 'official', 'Logo-Desa-Sungai-Meriam.png')
        if os.path.exists(path):
            return path
    static_root = getattr(settings, 'STATIC_ROOT', '')
    if static_root:
        path = os.path.join(static_root, 'assets', 'official', 'Logo-Desa-Sungai-Meriam.png')
        if os.path.exists(path):
            return path
    return None


def load_image_reader(file_field):
    """Load FileField/ImageField ke ImageReader. Mendukung storage lokal & cloud (Supabase/S3)."""
    try:
        local_path = file_field.path
        if os.path.exists(local_path):
            return ImageReader(local_path)
    except Exception:
        pass

    try:
        url = file_field.url
        if url.startswith('http://') or url.startswith('https://'):
            with urllib.request.urlopen(url, timeout=10) as response:
                data = response.read()
            return ImageReader(io.BytesIO(data))
    except Exception:
        pass

    return None


def draw_wrapped(p, text, x, y, max_width, font_size, line_height=0.52 * cm):
    p.setFont("Helvetica", font_size)
    max_chars = int(max_width / (font_size * 0.55))
    words, line = text.split(), ""
    for word in words:
        test = (line + " " + word).strip()
        if len(test) <= max_chars:
            line = test
        else:
            p.drawString(x, y, line)
            y -= line_height
            line = word
    if line:
        p.drawString(x, y, line)
        y -= line_height
    return y


def wrap_text(text, max_chars):
    words, lines, current = text.split(), [], ""
    for word in words:
        test = (current + " " + word).strip()
        if len(test) <= max_chars:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines or [""]


def draw_data_table(p, rows, x, y, col_label_w, col_val_w, line_height=0.52 * cm):
    sep_x     = x + col_label_w
    val_x     = sep_x + 0.5 * cm
    max_chars = int(col_val_w / (10 * 0.55))
    for label, value in rows:
        lines = wrap_text(str(value), max_chars)
        p.setFont("Helvetica-Bold", 10)
        p.drawString(x, y, label)
        p.setFont("Helvetica", 10)
        p.drawString(sep_x, y, ":")
        for i, vline in enumerate(lines):
            p.drawString(val_x, y - i * line_height, vline)
        y -= line_height * max(len(lines), 1)
    return y


def draw_kop_surat(p, width, height):
    """Kop surat (logo + nama pemerintahan + garis pembatas). Return posisi y setelahnya."""
    y = height - 1.5 * cm

    logo_path = get_logo_path()
    logo_size = 2.2 * cm
    logo_y    = y - logo_size + 0.3 * cm
    if logo_path:
        try:
            p.drawImage(logo_path, 1.8 * cm, logo_y,
                        width=logo_size, height=logo_size,
                        preserveAspectRatio=True, mask='auto')
        except Exception:
            pass

    p.setFont("Helvetica-Bold", 12)
    p.drawCentredString(width / 2, y, "PEMERINTAH DESA SUNGAI MERIAM")
    y -= 0.55 * cm
    p.setFont("Helvetica", 10)
    p.drawCentredString(width / 2, y, "Kecamatan Anggana, Kabupaten Kutai Kartanegara")
    y -= 0.45 * cm
    p.setFont("Helvetica", 9)
    p.drawCentredString(width / 2, y, "Provinsi Kalimantan Timur  –  Kode Pos 75381")
    y -= 0.4 * cm

    p.setLineWidth(2)
    p.line(1.8 * cm, y, width - 1.8 * cm, y)
    p.setLineWidth(0.5)
    p.line(1.8 * cm, y - 0.12 * cm, width - 1.8 * cm, y - 0.12 * cm)
    y -= 0.9 * cm
    return y


def draw_judul_surat(p, width, y, judul, reference_number):
    p.setFont("Helvetica-Bold", 11)
    p.drawCentredString(width / 2, y, judul)
    y -= 0.5 * cm
    p.setFont("Helvetica", 10)
    p.drawCentredString(width / 2, y, f"Nomor : {reference_number}")
    y -= 0.9 * cm
    return y


def draw_pemohon_data(p, user, profile, x, y, col_label_w, col_val_w, alamat_label="Alamat"):
    """Blok DATA PEMOHON dari profile user. `alamat_label` bisa dikustom per surat (mis. 'Alamat Asal')."""
    full_name     = user.get_full_name() or user.username
    nik           = getattr(profile, 'nik', '-') or '-'
    alamat        = getattr(profile, 'alamat', '-') or '-'
    rt            = getattr(profile, 'rt', '-') or '-'
    rw            = getattr(profile, 'rw', '-') or '-'
    dusun         = getattr(profile, 'dusun', '-') or '-'
    agama         = getattr(profile, 'agama', '-') or '-'
    pekerjaan     = getattr(profile, 'pekerjaan', '-') or '-'
    jk_raw        = getattr(profile, 'jenis_kelamin', '') or ''
    jenis_kelamin = 'Laki-laki' if jk_raw == 'L' else ('Perempuan' if jk_raw == 'P' else '-')
    tgl_lahir     = '-'
    if profile and getattr(profile, 'tanggal_lahir', None):
        tgl_lahir = profile.tanggal_lahir.strftime('%d %B %Y')

    alamat_lengkap = f"{alamat}, RT {rt}/RW {rw}, Dusun {dusun}"

    return draw_data_table(p, [
        ("Nama Lengkap",     full_name),
        ("NIK",              nik),
        ("Tempat/Tgl Lahir", tgl_lahir),
        ("Jenis Kelamin",    jenis_kelamin),
        ("Agama",            agama),
        ("Pekerjaan",        pekerjaan),
        (alamat_label,       alamat_lengkap),
    ], x, y, col_label_w, col_val_w)


def draw_signature_block(p, width, y, qr_code_field, tanggal_str):
    """Blok QR (kiri) + tanda tangan Kepala Desa (kanan)."""
    qr_size    = 3.5 * cm
    blok_y_top = y

    ttd_x = width - 7.5 * cm
    p.setFont("Helvetica", 10)
    p.drawString(ttd_x, blok_y_top, f"{NAMA_DESA}, {tanggal_str}")
    p.drawString(ttd_x, blok_y_top - 0.55 * cm, f"Kepala Desa {NAMA_DESA},")

    nama_y = blok_y_top - qr_size - 0.1 * cm
    p.setFont("Helvetica-Bold", 10)
    p.drawString(ttd_x, nama_y, KEPALA_DESA_NAME)
    p.setFont("Helvetica", 9)
    p.drawString(ttd_x, nama_y - 0.45 * cm, "Kepala Desa")

    qr_x = 1.8 * cm
    qr_y = nama_y - 0.1 * cm

    qr_drawn = False
    if qr_code_field:
        img_reader = load_image_reader(qr_code_field)
        if img_reader:
            try:
                p.drawImage(img_reader, qr_x, qr_y,
                            width=qr_size, height=qr_size,
                            preserveAspectRatio=True)
                p.setFont("Helvetica", 7.5)
                p.setFillColor(colors.grey)
                p.drawString(qr_x, qr_y - 0.35 * cm, "Scan untuk verifikasi keabsahan")
                p.setFillColor(colors.black)
                qr_drawn = True
            except Exception:
                pass

    if not qr_drawn:
        p.setStrokeColor(colors.lightgrey)
        p.setLineWidth(0.5)
        p.rect(qr_x, qr_y, qr_size, qr_size)
        p.setFont("Helvetica", 7)
        p.setFillColor(colors.lightgrey)
        p.drawCentredString(qr_x + qr_size / 2, qr_y + qr_size / 2, "QR Code")
        p.setFillColor(colors.black)
        p.setStrokeColor(colors.black)