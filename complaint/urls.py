from django.urls import path
from . import views

app_name = 'complaint'
urlpatterns = [
    path('', views.complaint_view, name='complaint'),
    path('sukses/', views.complaint_success_view, name='complaint_success'),
    path('riwayat/', views.complaint_history_view, name='complaint_history'),
]