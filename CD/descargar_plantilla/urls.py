from django.urls import path
from . import views

urlpatterns = [
    path('',views.descargar, name='descargar_plantilla'),
    #Descargar_Plantilla
    path('ajax/obtener_plantilla/', views.ajaxarchivo, name='obtener_plantilla'),
    path('ajax/ajaxareas/', views.ajaxareas, name='obtener_areas'),
    path('ajax/ajaxlineas/', views.ajax_linea, name='obtener_lineas'),
    path('ajax/ajaxrevision/',views.ajaxdetermine_revision, name='determinar_revicion'),
    path('ajax/ajaxcheckbox/', views.ajax_checkbox, name= 'ajax_checkbox'),
    path('ajax/ajaxnombre_doc/', views.nombre_doc_SelectedIndexChanged, name= 'ajax_nombre_doc'),
    path('ajax/ajaxbuton/', views.cD_Boton1_Click, name= 'ajax_btn'),
    path('ajax/ajaxblockdoc/', views.nombre_doc_SelectedIndexChanged, name= 'ajax_blockdoc'),
    

    



]
