from django.urls import path
from . import staff_views

app_name = 'complaint_staff'

urlpatterns = [
    path('', staff_views.staff_complaint_dashboard, name='dashboard'),
    path('detail/<int:pk>/', staff_views.staff_complaint_detail, name='detail'),
]