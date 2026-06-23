from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import StafDesa, KategoriStaf
from news.models import Pengumuman   
from gallery.models import GaleriPhoto


def home(request):
    template = 'core/index.html'

    # Ambil 3 berita terbaru — yang ditandai 'penting' selalu di urutan atas
    berita_terkini = Pengumuman.objects.all().order_by(
        '-is_penting', '-tanggal_dibuat'
    )[:3]

    galeri_preview = GaleriPhoto.objects.filter(ditampilkan=True).prefetch_related('tags')[:5] 

    context = {
        'title': 'Website Resmi Desa Sungai Meriam',
        'berita_terkini': berita_terkini,  
        'galeri_preview': galeri_preview, 
    }
    return render(request, template, context)


def village_profile(request):
    template_name = 'core/village_profile.html'
    context = {
        'title': 'Profil Desa | Website Resmi Desa Sungai Meriam',
    }
    return render(request, template_name, context)


def membership(request):
    template_name = 'core/membership.html'

    staffs   = StafDesa.objects.filter(aktif_tampil=True)
    q        = request.GET.get('q', '').strip()
    kategori = request.GET.get('kategori', '')

    if q:
        staffs = staffs.filter(
            Q(nama__icontains=q) | Q(jabatan__icontains=q)
        )
    if kategori and kategori in KategoriStaf.values:
        staffs = staffs.filter(kategori=kategori)

    kategori_choices = KategoriStaf.choices

    context = {
        'title'           : 'Keanggotaan | Website Resmi Desa Sungai Meriam',
        'staffs'          : staffs,
        'kategori_choices': kategori_choices,
        'active_kategori' : kategori,
        'search_query'    : q,
    }
    return render(request, template_name, context)


def detail_member(request, slug):
    template_name = 'core/detail_member.html'

    staff = get_object_or_404(
        StafDesa.objects.prefetch_related('penghargaan_list', 'umkm_list'),
        slug=slug,
        aktif_tampil=True,
    )

    staf_lain = StafDesa.objects.filter(
        aktif_tampil=True,
        kategori=staff.kategori
    ).exclude(pk=staff.pk)[:3]

    context = {
        'title'    : f"{staff.nama_lengkap} | Website Resmi Desa Sungai Meriam",
        'staff'    : staff,
        'staf_lain': staf_lain,
    }
    return render(request, template_name, context)