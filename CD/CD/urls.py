from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings
from CD import views

app_name = "CD"

urlpatterns = [
    #Adminstrador
    path('admin/', admin.site.urls),
    #Login
    path('', views.LoginView.as_view() ,name="login"),
    path('logout/', views.logout_view, name="logout"),  # Nueva URL para cerrar sesión
    
    
    #Inicio de Pagina
    path('inicio/',include("home.urls")),
    
    
    #Documentos
    path('aprobar/', include('aprobar_documento.urls')),
    path('agregar_documento/', include('agregar_documento.urls')),
    path('liberar_documento/', include('liberar_documento.urls')),
    path('bloquear_documento/', include('bloquear_documento.urls')),
    path('eliminar_documento/', include('eliminar_documento.urls')),
    path('descargar_plantilla/', include('descargar_plantilla.urls')),
    path('buscar_documento', include('buscar_documento.urls')),
    path('solicitar_firmas/', include('solicitar_firmas.urls')),
    path('bitacora/', include('bitacora.urls')),
    path('actualizar_documento/', include('actualizar_documento.urls')),


    
    #Entrenamiento
    path('entrenamiento/', include('realizar_entrenamiento.urls')),
    path('entrenamiento/aprobar_entraenamiento', include('aprobar_entrenamiento.urls')),
    path('entrenamiento/asignar_entrenamiento', include('asignar_entrenamiento.urls')),
    path('entrenamiento/matriz_de_entrenamiento', include('matriz_entrenamiento.urls')),
    path('entrenamiento/actualizar_nomenclatura', include('actualizar_nomenclatura.urls')),



    #apps de modelos usuarios y modelos
    path('usuarios/', include('Usuarios.urls')),
    path('documentos/', include('Documentos.urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

