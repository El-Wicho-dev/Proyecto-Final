from django.urls import path
from . import views

urlpatterns = [
    path("", views.adddrawing, name='add drawing'),
]