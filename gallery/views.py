from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import GaleriPhoto, Tag


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
        "page_obj": page_obj,
        "all_tags": all_tags,
        "active_tag": active_tag,
        "total_photos": total_photos,
    }
    return render(request, "gallery/galeri.html", context)