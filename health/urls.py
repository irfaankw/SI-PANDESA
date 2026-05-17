# health/urls.py
from django.urls import path
from . import views

app_name = 'health'

urlpatterns = [
    path('', views.appointment_view, name='appointment'),
    path('riwayat/', views.medical_history_view, name='medical_history'),
    path('checkin/<uuid:kode>/', views.qr_checkin_view, name='qr_checkin'),
    path('checkin/confirm/<int:pk>/', views.confirm_attendance_view, name='confirm_attendance'),
    
    # Dashboard Nakes
    path('nakes/', views.medical_dashboard_view, name='medical_dashboard'),
    path('nakes/input/<int:pk>/', views.medical_input_view, name='medical_input'),
]

# ─────────────────────────────────────────────────────────────────────────────
# URL Summary (base: /service/kesehatan/)
# ─────────────────────────────────────────────────────────────────────────────
# /service/kesehatan/                  → form buat janji
# /service/kesehatan/riwayat/          → riwayat berobat (profil user)
# /service/kesehatan/checkin/<uuid>/   → verifikasi QR (petugas scan)
# /service/kesehatan/nakes/            → dashboard nakes
# /service/kesehatan/nakes/input/<pk>/ → input diagnosa