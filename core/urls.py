from django.urls import path
from . import views

app_name = 'core'
urlpatterns = [
    path('', views.home, name='index'),
    path('village-profile/', views.village_profile, name='village_profile'),
    path('membership/', views.membership, name='membership'),
]