from django.urls import path
from . import views
urlpatterns = [
    path('', views.blockdoc, name='blockdocument'),
    path('desbloquear_documento/<str:nomenclatura>/', views.ajax_nomnenclatura , name= 'ajax_nomenclatura_desbloquear')

]
