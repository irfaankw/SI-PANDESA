import io
import qrcode
from django.core.files.base import ContentFile


def build_qr_code_file(data: str, filename: str) -> ContentFile:
    """
    Generate QR code PNG dari string `data`, dikembalikan sebagai ContentFile
    siap dipakai untuk FileField/ImageField.save().

    Dipanggil oleh BaseLetterRequest._generate_qr() — satu fungsi ini yang
    menangani QR untuk SELURUH jenis surat, jadi logikanya tidak perlu
    diduplikasi tiap kali bikin model surat baru.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    return ContentFile(buffer.read(), name=filename)