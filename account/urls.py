from django.urls import path
from . import views

app_name = 'account'
urlpatterns = [
    path('signin/', views.login_view, name='login'),
    path('signup/', views.register_view, name='register'),
    path('signout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
]