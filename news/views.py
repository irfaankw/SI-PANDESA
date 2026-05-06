from django.shortcuts import render

def index(request):
    template_name = 'news/index.html'
    context = {
        'title' : 'Berita & Pengumuman | Website Resmi Desa Sungai Meriam',
    }
    return render(request, template_name, context)