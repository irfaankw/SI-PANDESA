from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static 

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),

    # Auth & Account
    path('auth/', include('account.urls', namespace='account')),

    # Features
    path('market/', include('market.urls', namespace='market')),
    path('news/', include('news.urls', namespace='news')),
    path('service/', include('service.urls', namespace='service')),

    # Core
    path('', include('core.urls', namespace='core')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
