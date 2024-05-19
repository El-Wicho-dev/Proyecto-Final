from django.urls import path
from . import views

urlpatterns = [
    path("", views.actualizar_puestos, name='update_position'),
]