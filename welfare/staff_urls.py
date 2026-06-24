from django.urls import path
from . import staff_views

app_name = 'welfare_staff'

urlpatterns = [
    # Dashboard ringkasan — layanan/staff/kesejahteraan/
    path('', staff_views.staff_welfare_dashboard, name='dashboard'),

    # Kelola UMKM
    path('umkm/',                    staff_views.staff_umkm_list,   name='umkm_list'),
    path('umkm/<int:pk>/',           staff_views.staff_umkm_detail, name='umkm_detail'),
]