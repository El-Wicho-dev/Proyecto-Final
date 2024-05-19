from django.urls import path
from . import views
urlpatterns = [
    path("", views.aprobar, name='aprobar_entrenamiento'),
    path('ajax_documento_details/', views.ajaxdocument_details, name= 'document_details')
]