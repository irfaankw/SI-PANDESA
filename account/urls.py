from django.urls import path
from . import views

app_name = 'account'
urlpatterns = [
    path('keluar/', views.logout_view, name='logout'),
    path('profil/', views.profile_view, name='profile'),
    path('otp/request/', views.otp_request_view, name='otp_request'),
    path('otp/verify/', views.otp_verify_view, name='otp_verify'),
]