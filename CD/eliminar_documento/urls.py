from django.urls import path
from . import views
urlpatterns = [
    path('', views.deletedoc, name='deletedoc'),
    path('autocomplete_nomenclatura/', views.autocomplete_nomenclatura, name='autocomplete_nomenclatura'),

]
