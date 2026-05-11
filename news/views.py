from django.shortcuts import render

def news_list(request):
    template_name = 'news/news.html'
    context = {
        'title' : 'Berita & Pengumuman | Website Resmi Desa Sungai Meriam',
    }
    return render(request, template_name, context)