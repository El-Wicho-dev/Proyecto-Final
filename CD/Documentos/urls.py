from django.urls import path
from . import views
urlpatterns = [
    path('agregardocumento/', views.adddoc, name='adddoc'),
    
]
