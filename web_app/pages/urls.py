from django.urls import path
from . import views

urlpatterns = [
    path('', lambda request: views.url_redirect(request), name="home"),
    path("drive", views.home, name="home"),
    path("drive/delete/<str:file_id>", views.delete, name="delete"),
    path("drive/path/<str:file_id>", views.path, name="path"),
    path("drive/imprint", views.imprint, name="imprint"),
]
