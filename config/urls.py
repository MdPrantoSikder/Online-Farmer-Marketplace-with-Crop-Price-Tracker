from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    
     path("", include("apps.marketplace.urls")),  # Make sure the correct app is included
    path("api/home/", include("apps.marketplace.urls")),
    path("accounts/", include("apps.accounts.urls")),
    path("farmers/", include("apps.farmers.urls")),
    path("admin/", admin.site.urls),
]

# serve media in dev
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
