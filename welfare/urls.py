# welfare/urls.py
from django.urls import path
from . import views

app_name = 'welfare'

urlpatterns = [
    path('',                            views.kesejahteraan_view,  name='kesejahteraan'),
    path('kelola-toko/',                views.kelola_toko_view,    name='kelola_toko'),
    path('kelola-toko/tambah-produk/',  views.tambah_produk_view,  name='tambah_produk'),
    path('kelola-toko/edit/<int:produk_id>/',  views.edit_produk_view,   name='edit_produk'),
    path('kelola-toko/hapus/<int:produk_id>/', views.hapus_produk_view,  name='hapus_produk'),
]