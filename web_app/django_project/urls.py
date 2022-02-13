from django.contrib import admin
from django.urls import path, include  # new
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("pages.urls")),  # new
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
