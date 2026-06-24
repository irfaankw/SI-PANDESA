from django.urls import path
from . import staff_views

app_name = 'service_staff'

urlpatterns = [
    path('', staff_views.staff_letter_dashboard, name='letter_dashboard'),
    path('detail/<str:slug>/<str:ref>/', staff_views.staff_letter_detail, name='letter_detail'),
]