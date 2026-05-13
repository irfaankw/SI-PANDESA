from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import StafDesa, KategoriStaf


def home(request):
    template = 'core/index.html'
    context = {
        'title': 'Website Resmi Desa Sungai Meriam'
    }
    return render(request, template, context)


def village_profile(request):
    template_name = 'core/village_profile.html'
    context = {
        'title': 'Profil Desa | Website Resmi Desa Sungai Meriam',
    }
    return render(request, template_name, context)


def membership(request):
    """
    Halaman direktori perangkat desa.
    Mendukung filter kategori (via GET ?kategori=...) dan
    pencarian (via GET ?q=...) sebagai fallback server-side
    di samping Alpine.js client-side.
    """
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
    """
    Halaman profil detail satu staf desa.
    URL: /membership/<slug>/
    Menggunakan prefetch_related agar query penghargaan & UMKM
    tidak N+1 (efisien).
    """
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