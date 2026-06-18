from django.urls import path
from . import views

app_name = 'market'

urlpatterns = [
    path('',views.belanja_view,name='market_belanja'),
    path('produk/<int:produk_id>/', views.detail_produk_view,  name='detail_produk'),
]