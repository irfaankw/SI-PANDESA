from django.urls import path
from . import views

app_name = 'core'
urlpatterns = [
    path('', views.index, name='index'),
    path('profil-desa/', views.village_profile, name='profile'),
    path('keanggotaan/', views.membership, name='anggota'),
]