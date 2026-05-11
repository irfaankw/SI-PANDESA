from django.shortcuts import render

def service_list(request):
    template_name = 'service/service.html'
    context = {
        'title' : 'Service | Website Resmi Desa Sungai Meriam',
    }
    return render(request, template_name, context)