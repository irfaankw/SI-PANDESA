from django.urls import path
from . import staff_views

app_name = 'account_staff'

urlpatterns = [
    path('', staff_views.staff_profile_dashboard, name='dashboard'),
    path('detail/<int:pk>/', staff_views.staff_profile_detail, name='detail'),
]