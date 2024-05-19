from django.urls import path
from . import views
urlpatterns = [
    path('',views.solicitar, name='solicitar'),
    path('ajax_filtrar_usuarios',views.ajax_filtrar_usuarios, name='ajax_filtrar'),
    path('send-email/', views.send_test_email),

]
