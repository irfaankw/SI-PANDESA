from django.urls import path
from . import views
from gallery import views as gallery_views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='index'),
    path('profil-desa/', views.village_profile, name='village_profile'),
    path('keanggotaan/', views.membership, name='membership'),
    path('keanggotaan/<slug:slug>/', views.detail_member, name='detail_member'),

    # ── Galeri ────────────────────────────────────────────────
    path('galeri/', gallery_views.galeri_list, name='galeri'),
]