from django.urls import path
from . import views
urlpatterns = [
    path("", views.update_document, name='update_document'),
    path('autocomplete_nomenclatura/', views.autocomplete_nomenclatura, name='autocomplete_nomenclatura_update'),

]