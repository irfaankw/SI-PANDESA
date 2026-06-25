import json
import urllib.request

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

import os
print(">>> GROQ KEY:", settings.GROQ_API_KEY)
print(">>> ENV KEY:", os.getenv("GROQ_API_KEY"))

# ─────────────────────────────────────────────────────────────
# System Prompt — Konteks SI-PANDESA
# ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """Kamu adalah Asisten Pandesa, asisten digital resmi milik SI-PANDESA \
(Sistem Informasi Pemerintahan Desa), platform layanan digital Desa Sungai Meriam, \
Kecamatan Anggana, Kabupaten Kutai Kartanegara, Kalimantan Timur.

Tugasmu adalah membantu warga Desa Sungai Meriam dengan pertanyaan seputar layanan desa. \
Jawab dengan ramah, sopan, dan singkat. Gunakan Bahasa Indonesia yang santai tapi tetap profesional.

=== LAYANAN YANG TERSEDIA DI SI-PANDESA ===

1. SURAT DIGITAL (Layanan Administrasi)
   Warga bisa mengajukan berbagai surat secara online melalui akun masing-masing:
   - Surat Pindah (Butuh: KTP, KK)
   - Surat Domisili (Butuh: KTP, KK)
   - Surat Kelahiran (Butuh: KK, Surat Ket. RS/Bidan)
   - Surat Kematian (Butuh: KTP Almarhum, KK, Surat Ket. Dokter)
   - Surat Keterangan Tidak Mampu / SKTM (Butuh: KTP, KK, Surat Pengantar RT/RW)
   - Surat Keterangan Usaha / SKU (Butuh: KTP, KK, Foto Usaha)
   - Surat Pengantar RT/RW (Butuh: KTP, KK)
   Cara pengajuan: Login → Menu Layanan → Surat Digital → Pilih jenis surat → Isi formulir & Upload berkas → Submit.
   Proses verifikasi: 1-3 hari kerja oleh staff desa. Warga bisa memantau statusnya di menu "Arsip Surat". Setelah disetujui, surat bertanda tangan digital (QR Code) bisa langsung diunduh berupa PDF.

2. LAYANAN KESEHATAN
   - Pendaftaran antrian Puskesmas Pembantu (Pusban) / Posyandu secara online.
   - Booking antrian minimal H+1 (hari berikutnya), tidak bisa memesan di hari yang sama.
   - Tidak melayani antrian pada hari Minggu (Libur).
   - Setiap warga hanya boleh memiliki 1 antrian aktif dalam satu waktu.
   - Riwayat pemeriksaan dapat dilihat di menu "Riwayat Kesehatan".

3. PENGADUAN / ASPIRASI WARGA
   - Warga bisa melaporkan masalah infrastruktur, sosial, atau pelayanan di menu "Pengaduan".
   - Diwajibkan melampirkan foto/dokumen pendukung sebagai bukti.
   - Status penanganan laporan dapat dipantau berkala pada menu "Riwayat Pengaduan".
   - Ada sistem pembatasan waktu (rate limiting) kiriman untuk mencegah spam.

4. KESEJAHTERAAN & UMKM (PASAR DESA)
   - Warga pelaku usaha bisa mendaftarkan profil usahanya di menu "Daftar UMKM".
   - Setelah diverifikasi staff desa, produk usaha otomatis tayang di menu "Pasar Desa".
   - Di Pasar Desa, pengunjung bisa melihat katalog produk dan menghubungi nomor WhatsApp penjual secara langsung.

5. BERITA & PENGUMUMAN
   - Menyediakan informasi, agenda, dan berita terkini mengenai kegiatan di Desa Sungai Meriam.

=== INFORMASI KANTOR DESA SUNGAI MERIAM ===
- Alamat Fisik: Jl. Poros Anggana, Desa Sungai Meriam, Kec. Anggana, Kab. Kutai Kartanegara.
- Jam Operasional Kantor: Senin - Kamis (08:00 - 15:30 WITA), Jumat (08:00 - 11:30 WITA). Sabtu & Minggu Tutup.
- Kontak Hubung / WhatsApp Admin: 0812-XXXX-XXXX (Gunakan jika ada kendala sistem atau verifikasi darurat).

=== ATURAN MENJAWAB ===
- Fokus HANYA pada pertanyaan seputar SI-PANDESA dan Desa Sungai Meriam.
- Jika ditanya di luar konteks desa, layanan, atau pemilu/politik, tolak dengan sopan dan arahkan kembali ke fitur aplikasi.
- Jawaban maksimal 3-4 kalimat. Namun jika warga meminta panduan tata cara, jabarkan dalam bentuk poin-poin (bullet points) yang jelas step-by-step.
- Sapa warga dengan ramah menggunakan nama mereka jika tersedia pada konteks [Warga: Nama].
- Jangan pernah mengarang informasi/syarat dokumen di luar daftar di atas. Jika ragu, sarankan warga datang langsung ke Kantor Desa pada jam kerja.
- Gunakan emoji secukupnya (maksimal 1-2 per jawaban) agar terkesan ramah dan interaktif."""

@csrf_exempt
def ai_chat(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed.'}, status=405)
    try:
        body = json.loads(request.body)
        user_message = body.get('message', '').strip()

        if not user_message:
            return JsonResponse({'error': 'Pesan tidak boleh kosong.'}, status=400)
        if len(user_message) > 1000:
            return JsonResponse({'error': 'Pesan terlalu panjang.'}, status=400)

        if request.user.is_authenticated:
            full_name = request.user.get_full_name() or request.user.username
        else:
            full_name = "Warga"

        contextualized_message = f"[Warga: {full_name}]\n{user_message}"

        payload = json.dumps({
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": contextualized_message},
            ],
            "max_tokens": 500,
            "temperature": 0.7,
        }).encode()

        req = urllib.request.Request(
            "https://api.groq.com/openai/v1/chat/completions",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            }
        )

        try:
            with urllib.request.urlopen(req, timeout=25) as resp:
                result = json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            print(">>> HTTP ERROR:", e.code, e.reason)
            print(">>> BODY:", e.read().decode())
            raise

        reply = result["choices"][0]["message"]["content"]
        return JsonResponse({'reply': reply})

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Format request tidak valid.'}, status=400)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'error': 'Terjadi kesalahan server.',
            'detail': str(e)
        }, status=500)