from django.shortcuts import render

def index(request):
    template_name = 'market/index.html'
    context = {
        'title' : 'Belanja | Website Resmi Desa Sungai Meriam',
    }
    return render(request, template_name, context)