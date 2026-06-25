from django.urls import path
from . import staff_views

app_name = 'welfare_staff'

urlpatterns = [
    # Dashboard ringkasan — layanan/staff/kesejahteraan/
    path('', staff_views.staff_welfare_dashboard, name='dashboard'),

    # Kelola UMKM
    path('umkm/',                    staff_views.staff_umkm_list,   name='umkm_list'),
    path('umkm/<int:pk>/',           staff_views.staff_umkm_detail, name='umkm_detail'),

    path('bansos/',                       staff_views.staff_bansos_dashboard,   name='bansos_dashboard'),
    path('bansos/program/tambah/',        staff_views.staff_program_tambah,     name='program_tambah'),
    path('bansos/program/<int:pk>/edit/', staff_views.staff_program_edit,       name='program_edit'),
    path('bansos/program/<int:pk>/toggle/', staff_views.staff_program_toggle,   name='program_toggle'),
    path('bansos/pengajuan/',             staff_views.staff_pengajuan_list,     name='pengajuan_list'),
    path('bansos/pengajuan/<int:pk>/',    staff_views.staff_pengajuan_detail,   name='pengajuan_detail'),
]