# jec/urls.py

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('buin/', include('buin.urls')),
]

# Menambahkan URL untuk mengakses file media
if settings.DEBUG:  # Pastikan hanya diaktifkan pada mode development (DEBUG=True)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
