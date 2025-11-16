
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from .views import tinymce_upload

urlpatterns = [
    path('admin/', admin.site.urls),
    path('tinymce/', include('tinymce.urls')),
    path('tinymce/upload/', tinymce_upload),
    path('', include('shop.urls')),
    path('cart/', include('carts.urls')),
    path('auth/', include('accounts.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

