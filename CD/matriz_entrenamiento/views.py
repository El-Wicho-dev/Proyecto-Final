from django.shortcuts import render
from func.loading import cargar_matriz
from django.db.models import F, Value, CharField,Case,When
from django.db.models.functions import Concat, Cast
from Entrenamiento.models import Entrenamiento,EntrenamientoPuestoNomenclatura,Firma
from Documentos.models  import Documento,Plantilla
from Usuarios.models import UnidadNegocio,Puesto,UsuarioPuesto,PerfilUsuario
# Create your views here.

#se rendiraza la matriz de entrenamiento
def matriz(request):
    template = 'Entrenamiento/matriz_de_entrenamiento.html'
    
    #Manda allmar el metodo de cargar matriz
    data = cargar_matriz()

   
    context = {
       'columns': data['columns'],
       'rows': data['rows'],
       'total_porcentaje': data['total_porcentaje'],  # Pasar el porcentaje total al contexto
    }
    return render(request,template,context)






