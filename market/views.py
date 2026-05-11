from django.shortcuts import render

def market_home(request):
    template_name = 'market/market.html'
    context = {
        'title' : 'Belanja | Website Resmi Desa Sungai Meriam',
    }
    return render(request, template_name, context)