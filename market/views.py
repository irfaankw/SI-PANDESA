from django.shortcuts import render

def index(request):
    template_name = 'market/index.html'
    context = {
        'title' : 'Belanja | Website Resmi Desa Sungai Meriam',
    }
    return render(request, template_name, context)

def pembeli(request):
    tamplate_name = 'market/pembeli.html'
    context = {
        'title' : 'pembeli / belanja / website resmi desa sungai mariam',
    }
    return render(request, tamplate_name, context)
