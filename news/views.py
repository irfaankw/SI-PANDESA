from django.shortcuts import render,get_object_or_404
from .models import Pengumuman

def news_list(request):
    # 1. Ambil kategori dari parameter URL (contoh: ?kategori=LAYANAN)
    kategori_filter = request.GET.get('kategori', 'SEMUA')
    query_pencarian = request.GET.get('search', '')
    
    # 2. Ambil data dasar berdasarkan filter kategori
    if kategori_filter != 'SEMUA':
        semua_berita = Pengumuman.objects.filter(kategori=kategori_filter).order_by('-is_penting', '-tanggal_dibuat')
    else:
        semua_berita = Pengumuman.objects.all().order_by('-is_penting', '-tanggal_dibuat')

    if query_pencarian:
        semua_berita = semua_berita.filter(judul__icontains=query_pencarian)

    # 3. Logika pemisahan untuk Desain (Sesuai Screenshot 2026-05-13 125756.jpg)
    # Kita ambil 1 berita terbaru yang ditandai 'is_penting=True' sebagai headline
    berita_penting = semua_berita.filter(is_penting=True).first()
    
    # Sisanya adalah berita biasa (kita exclude berita_penting agar tidak muncul dua kali)
    if berita_penting:
        berita_biasa = semua_berita.exclude(id=berita_penting.id)
    else:
        berita_biasa = semua_berita

    # 4. Masukkan ke context
    context = {
        'title': 'Berita & Pengumuman | Website Resmi Desa Sungai Meriam',
        'berita_penting': berita_penting, # Untuk bagian atas yang besar
        'berita_biasa': berita_biasa,     # Untuk bagian grid di bawahnya
        'kategori_aktif': kategori_filter,
        'kategori_list': ['SEMUA', 'PENGUMUMAN', 'KEGIATAN', 'LAYANAN', 'PERINGATAN'],
        'query_pencarian': query_pencarian,
    }
    
    return render(request, 'news/news.html', context)

def news_detail(request, pk):
    # Mengambil satu berita berdasarkan Primary Key (id)
    # Jika tidak ditemukan, Django otomatis melempar halaman error 404
    berita = get_object_or_404(Pengumuman, pk=pk)
    
    context = {
        'title': f'{berita.judul} | Desa Sungai Meriam',
        'berita': berita,
    }
    return render(request, 'news/detail.html', context)