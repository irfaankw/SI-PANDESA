from django.shortcuts import render

def index(request):
    template = 'core/index.html'
    context = {
        'title' : 'Website Resmi Desa Sungai Meriam'
    }
    return render(request, template, context)

def village_profile(request):
    template_name = 'core/village_profile.html'
    context = {
        'title' : 'Profil Desa | Website Resmi Desa Sungai Meriam',
    }
    return render(request, template_name, context)

def membership(request):
    template_name = 'core/membership.html'
    context = {
        'title' : 'Keanggotaan | Website Resmi Desa Sungai Meriam',
    }
    return render(request, template_name, context)