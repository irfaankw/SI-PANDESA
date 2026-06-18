from django.urls import path
from . import views

app_name = 'service'
urlpatterns = [
    # ── Index layanan surat ───────────────────────────────────
    path('', views.digital_mail_index, name='mail_index'),

    # ── Surat Pindah ──────────────────────────────────────────
    path('surat-pindah/', views.move_letter_view, name='move_letter'),
    path('surat-pindah/unduh/<str:ref>/', views.download_move_letter_pdf, name='download_move_letter'),

    # ── Surat Domisili ─────────────────────────────────────────
    path('surat-domisili/', views.domicile_letter_view, name='domicile_letter'),
    path('surat-domisili/unduh/<str:ref>/', views.download_domicile_letter_pdf, name='download_domicile_letter'),

    # ── Surat Kematian ─────────────────────────────────────────
    path('surat-kematian/', views.death_letter_view, name='death_letter'),
    path('surat-kematian/unduh/<str:ref>/', views.download_death_letter_pdf, name='download_death_letter'),

    # ── Surat Kelahiran ────────────────────────────────────────
    path('surat-kelahiran/', views.birth_letter_view, name='birth_letter'),
    path('surat-kelahiran/unduh/<str:ref>/', views.download_birth_letter_pdf, name='download_birth_letter'),

    # ── Surat Tidak Mampu ───────────────────────────────────────
   path('surat-tidak-mampu/', views.poverty_letter_view, name='poverty_letter'),
   path('surat-tidak-mampu/unduh/<str:ref>/', views.download_poverty_letter_pdf, name='download_poverty_letter'),

   # ── Surat Keterangan Usaha ───────────────────────────────────
   path('surat-usaha/', views.business_letter_view, name='business_letter'),
   path('surat-usaha/unduh/<str:ref>/', views.download_business_letter_pdf, name='download_business_letter'),

   # ── Surat Pengantar ──────────────────────────────────────────
   path('surat-pengantar/', views.intro_letter_view, name='intro_letter'),
   path('surat-pengantar/unduh/<str:ref>/', views.download_intro_letter_pdf, name='download_intro_letter'),
]