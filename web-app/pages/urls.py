from django.urls import path
from . import views

urlpatterns = [
    path("drive", views.home, name="home"),
    path("drive/delete/<str:file_id>", views.delete, name="delete"),
    path("drive/imprint", views.imprint, name="imprint"),
]
