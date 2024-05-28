from django.urls import path
from . import views

urlpatterns = [
    path("", views.actualizar_nomenclatura, name='update_nomenclature'),
    path("elimnar_nomenclatura/", views.eliminar_nomenclatura, name='delete_nomenclature'),
    path('ajaxpuesto/',views.puestoajax, name='ajax_puesto_nomenclatura'),
    path('ajaxusuarios/',views.obtener_datos_usuarios, name='ajax_usuarios_get_nomenclatura'),
    path('obtener_usuarios_por_puesto/',views.obtener_usuarios_por_puesto, name='obtener_usuarios_por_puesto'),
    

]