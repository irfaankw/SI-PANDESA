from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator
from .models import StafDesa, KategoriStaf, GaleriPhoto, Tag
from news.models import Pengumuman


def home(request):
    template = 'core/index.html'

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
    context = {
        'title': 'Profil Desa | Website Resmi Desa Sungai Meriam',
    }
    return render(request, 'core/village_profile.html', context)


def membership(request):
    staffs   = StafDesa.objects.filter(aktif_tampil=True).select_related('user')
    q        = request.GET.get('q', '').strip()
    kategori = request.GET.get('kategori', '')

    if q:
        staffs = staffs.filter(
            Q(nama__icontains=q) | Q(jabatan__icontains=q)
        )
    if kategori and kategori in KategoriStaf.values:
        staffs = staffs.filter(kategori=kategori)

    context = {
        'title'           : 'Keanggotaan | Website Resmi Desa Sungai Meriam',
        'staffs'          : staffs,
        'kategori_choices': KategoriStaf.choices,
        'active_kategori' : kategori,
        'search_query'    : q,
    }
    return render(request, 'core/membership.html', context)


def detail_member(request, slug):
    staff = get_object_or_404(
        StafDesa.objects.select_related('user', 'user__umkm'),
        slug=slug,
        aktif_tampil=True,
    )

    # welfare.UMKM milik staf ini (None kalau tidak punya akun / belum daftar UMKM)
    umkm = staff.umkm  # property di model, sudah handle try/except

    # Produk aktif dari UMKM-nya (kosong kalau umkm None atau belum aktif)
    produk_list = []
    if umkm and umkm.status == 'aktif':
        produk_list = umkm.produk.filter(aktif=True).order_by('-created_at')

    staf_lain = StafDesa.objects.filter(
        aktif_tampil=True,
        kategori=staff.kategori
    ).exclude(pk=staff.pk)[:3]

    context = {
        'title'      : f"{staff.nama_lengkap} | Website Resmi Desa Sungai Meriam",
        'staff'      : staff,
        'umkm'       : umkm,
        'produk_list': produk_list,
        'staf_lain'  : staf_lain,
    }
    return render(request, 'core/detail_member.html', context)


def galeri_list(request):
    tag_slug = request.GET.get("tag", "")
    photos = GaleriPhoto.objects.filter(ditampilkan=True).prefetch_related("tags")

    active_tag = None
    if tag_slug:
        active_tag = get_object_or_404(Tag, slug=tag_slug)
        photos = photos.filter(tags=active_tag)

    all_tags = Tag.objects.all()
    total_photos = GaleriPhoto.objects.filter(ditampilkan=True).count()

    paginator = Paginator(photos, 8)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj"    : page_obj,
        "all_tags"    : all_tags,
        "active_tag"  : active_tag,
        "total_photos": total_photos,
    }
    return render(request, "core/galeri.html", context)