from django.urls import path
from . import views

urlpatterns = [
    path('liberar/',views.liberar,name='liberar-documento'),   
    path('ajax_documento_details/', views.ajaxdocument_details, name= 'document_details_liberar')

]
