from django.urls import path
from . import staff_views

app_name = 'core_staff'

urlpatterns = [
    path('',              staff_views.staff_anggota_list,   name='dashboard'),
    path('tambah/',       staff_views.staff_anggota_tambah, name='tambah'),
    path('<int:pk>/edit/',   staff_views.staff_anggota_edit,   name='edit'),
    path('<int:pk>/hapus/',  staff_views.staff_anggota_hapus,  name='hapus'),
]