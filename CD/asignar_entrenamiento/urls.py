from django.urls import path
from . import views 
urlpatterns = [
    path('',views.asignar_entrenamiento, name='asignar_entrenamiento'),
    path('ajaxpuesto/',views.puestoajax, name='ajax_puesto'),
    path('ajaxusuarios/',views.obtener_datos_usuarios, name='ajax_usuarios_get'),
    
    
]
