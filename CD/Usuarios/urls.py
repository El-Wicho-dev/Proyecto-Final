from django.urls import path
from . import views
urlpatterns = [
    path('agregar_usuario/',views.adduser,name='adduser'),   
    path('agregar_usuario/agregar_perfil/<int:user_id>/',views.add_profile,name='add_profile'),  
    path('bloquear_usuario/',views.blockuser,name='blockuser'),   

]
