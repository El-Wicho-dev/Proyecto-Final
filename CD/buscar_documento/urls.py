from django.urls import path
from . import views

urlpatterns = [
    path('',views.buscar, name='buscar_documento'),
    path('ajax/obtener_plantilla/', views.ajaxarchivo, name='obtener_plantilla_buscar'),
    path('ajax/ajaxareas/', views.ajaxareas, name='obtener_areas_buscar'),
    path('ajax/ajaxlineas/', views.ajax_linea, name='obtener_lineas_buscar'),

]
