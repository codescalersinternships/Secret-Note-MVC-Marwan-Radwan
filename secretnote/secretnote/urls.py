from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path("secret-note", views.create_note, name="create_note"),
    path("secret-note/<str:id>", views.get_note, name="get_note"),
]
