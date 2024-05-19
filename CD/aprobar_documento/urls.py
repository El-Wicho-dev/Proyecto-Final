from django.urls import path
from . import views
from django.conf import settings

urlpatterns = [
    path('', views.aprobar, name='aprobar'),
    path('get-document-url/', views.get_document_url, name='get-document-url'),

]


