from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='index'),
    path('village-profile/', views.village_profile, name='village_profile'),

    # Membership: list + detail via slug
    path('membership/', views.membership, name='membership'),
    path('membership/<slug:slug>/', views.detail_member, name='detail_member'),
]