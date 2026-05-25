from django.shortcuts import render, get_object_or_404
from welfare.models import Produk, UMKM


def belanja_view(request):
    kategori_aktif  = request.GET.get('kategori', '')
    query           = request.GET.get('q', '').strip()

    produk_qs = Produk.objects.filter(
        aktif=True,
        umkm__status='aktif'
    ).select_related('umkm', 'umkm__pemilik', 'umkm__pemilik__profile')

    if kategori_aktif:
        produk_qs = produk_qs.filter(kategori=kategori_aktif)

    if query:
        produk_qs = produk_qs.filter(nama__icontains=query)

    total_produk     = Produk.objects.filter(aktif=True, umkm__status='aktif').count()
    total_umkm       = UMKM.objects.filter(status='aktif').count()
    kategori_choices = Produk.KATEGORI_CHOICES

    return render(request, 'market/market.html', {
        'title':            'Belanja Desa',
        'produk_list':      produk_qs,
        'kategori_aktif':   kategori_aktif,
        'kategori_choices': kategori_choices,
        'query':            query,
        'total_produk':     total_produk,
        'total_umkm':       total_umkm,
    })


def detail_produk_view(request, produk_id):
    produk = get_object_or_404(
        Produk, id=produk_id, aktif=True, umkm__status='aktif'
    )

    produk_lain = Produk.objects.filter(
        umkm=produk.umkm, aktif=True
    ).exclude(id=produk.id)[:4]

    # Buat link WhatsApp
    no_wa = produk.no_wa_pemilik.replace('-', '').replace(' ', '').replace('+', '')
    if no_wa.startswith('0'):
        no_wa = '62' + no_wa[1:]
    pesan_wa = (
        f"Halo, saya tertarik dengan produk *{produk.nama}* "
        f"dari toko *{produk.umkm.nama_usaha}* "
        f"seharga Rp {produk.harga:,}. "
        f"Apakah masih tersedia?"
    )
    link_wa = f"https://wa.me/{no_wa}?text={pesan_wa}"

    return render(request, 'market/detail_produk.html', {
        'title':       produk.nama,
        'produk':      produk,
        'produk_lain': produk_lain,
        'link_wa':     link_wa,
    })