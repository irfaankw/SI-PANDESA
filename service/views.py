from django.shortcuts import render

def index(request):
    template_name = 'service/index.html'
    context = {
        'title' : 'Service | Website Resmi Desa Sungai Meriam',
    }
    return render(request, template_name, context)