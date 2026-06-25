from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from service import views as service_views
from core import ai_views
from core import lacak_views 

urlpatterns = [
    # ── Admin Django ──────────────────────────────────────────
    path("admin/", admin.site.urls),

    # ── Auth & Account ────────────────────────────────────────
    path('auth/', include('account.urls', namespace='account')),
    path('accounts/', include('allauth.urls')),

    # ── Fitur Publik ──────────────────────────────────────────
    path('pasar/',   include('market.urls', namespace='market')),
    path('berita/',  include('news.urls',   namespace='news')),

    # ── Layanan Warga ─────────────────────────────────────────
    path('layanan/surat/',         include('service.urls',   namespace='service')),
    path('layanan/kesehatan/',     include('health.urls',    namespace='health')),
    path('layanan/pengaduan/',     include('complaint.urls', namespace='complaint')),
    path('layanan/kesejahteraan/', include('welfare.urls',   namespace='welfare')),

    # ── Dashboard Staff Desa ───────────────────────────────────
    path('layanan/staff/warga/',         include('account.staff_urls',   namespace='account_staff')),
    path('layanan/staff/surat/',         include('service.staff_urls',   namespace='service_staff')),
    path('layanan/staff/pengaduan/',     include('complaint.staff_urls', namespace='complaint_staff')),
    path('layanan/staff/kesejahteraan/', include('welfare.staff_urls',   namespace='welfare_staff')),

    # ── Lacak Pengajuan ───────────────────────────────────
    path('layanan/lacak/', lacak_views.lacak_view, name='lacak_pengajuan'),

    # ── Verifikasi QR — publik, tanpa login ───────────────────
    path('layanan/verifikasi/<str:ref>/', service_views.verify_letter_view, name='verify_letter'),

    # ── AI Chatbot ────────────────────────────────────────────
    path('api/ai/chat/', ai_views.ai_chat, name='ai_chat'),

    # ── Core (beranda, profil desa, dll) ──────────────────────
    path('', include('core.urls', namespace='core')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,  document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,   document_root=settings.MEDIA_ROOT)