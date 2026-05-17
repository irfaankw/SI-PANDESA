from django.urls import path
from . import views

app_name = 'account'
urlpatterns = [
    path('masuk/', views.login_view, name='login'),
    path('daftar/', views.register_view, name='register'),
    path('keluar/', views.logout_view, name='logout'),
    path('profil/', views.profile_view, name='profile'),
]