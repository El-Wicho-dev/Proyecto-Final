from django.shortcuts import render
from Documentos.models import Plantilla,Documento
from Usuarios.models import Area,Linea
from Documentos.forms import PlantillaForm
from Usuarios.forms import AreaForm,LineaForm
from django.http import JsonResponse,FileResponse,Http404,HttpResponse
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.models import F, Value, CharField, Func, Case, When
from django.db.models.functions import Concat
from func.clases_de_documento import nomenclatura
import subprocess

from docx import Document

import os
from django.conf import settings


# Create your views here.
from django.shortcuts import render, redirect

#ME QUE DE AQUI ARREGLANGO EL BUEGEO
# Create your views here.
def buscar(request):
    plantillas_habilitadas = Plantilla.objects.filter(estado='HABILITADO').order_by('nombre')
    areas_habilitadas = Area.objects.all().order_by('area')
    lineas_habilitadas = Linea.objects.all().order_by('nombre_linea')  
    
    plantila_form = PlantillaForm(request.GET or None)
    area_form = AreaForm(request.GET or None)
    linea_form = LineaForm(request.GET or None)
    
    print(request.GET)
    print(request.POST)
    if request.method == 'GET':
        action = request.GET.get('action')
        print(action)  # Imprime el valor de 'action' en la consola para verificación
        
        area =  request.GET.get('areaSeleccionada')
        plantilla = request.GET.get('plantillaSeleccionada')
        linea = request.GET.get('lineaSeleccionada')
        nombre_documento = request.GET.get("nombreDocumento")
        

        print(nombre_documento)
        if action == 'search':
            if nombre_documento:
                print("Si entre xd")
                try:
                    codigo_plantilla, codigo_linea, consecutivo, rev, nombre = nomenclatura(nombre_documento)
                    print('CODIGO', codigo_plantilla, 'CODIGO_LINEA', codigo_linea, 'TU CONSECUITVO:', consecutivo, 'REV', rev, 'NOMBRE', nombre)
                    
                    documentos = Documento.objects.filter(
                        id_plantilla__codigo=codigo_plantilla,
                        id_linea__codigo_linea=codigo_linea,
                        nombre=nombre,
                        estado='APROBADO',
                        consecutivo=consecutivo
                    )
                    
                    if documentos.exists():
                        print("si encontre")
                        messages.success(request, "Documentos encontrados.")
                        for doc in documentos:
                            print(doc.id)
                            
                        abrir_documento(plantilla,linea,nombre_documento)
                        
                    else:
                        messages.info(request, "No se encontraron documentos con los criterios especificados.")
                
                except ValueError as e:
                    messages.error(request, str(e))
                except Exception as e:
                    messages.error(request, f"Error inesperado: {str(e)}")
    
    context = {
        'plantila_form': plantila_form,
        'area_form': area_form,
        'linea_form': linea_form,
        'plantillas_habilitadas': plantillas_habilitadas,
        'areas_habilitadas': areas_habilitadas,
        'lineas_habilitadas': lineas_habilitadas,
    }
    return render(request, 'documentos/buscar_documento.html', context)



def abrir_documento(plantilla,linea,nombre_documento):
   
    file_path = os.path.join(settings.MEDIA_ROOT, 'Control_de_documentos_Editables', plantilla, linea, nombre_documento)
    
    if os.path.exists(file_path):
        try:
            # Ejecutar LibreOffice para abrir el documento
            subprocess.run(['libreoffice', file_path])
            return HttpResponse("El documento se está abriendo con LibreOffice.")
        except Exception as e:
            return HttpResponse(f"Error al abrir el documento: {e}")
    else:
        return HttpResponse("El archivo no existe.", status=404)

#obtener areas
def ajaxarchivo(request):
    tipo_de_plantilla = request.GET.get('nombre')
    area_seleccionada = request.GET.get('area')
    getid = Plantilla.objects.get(nombre=tipo_de_plantilla)
    id_plantilla = getid.id
    #print(id_plantilla)
    
   

    try:
        plantilla = Plantilla.objects.get(nombre=tipo_de_plantilla)
        tipo_de_archivo = plantilla.tipo_de_area
        codigo_plantilla = plantilla.codigo
        #print(f'tipo de archivo es:  {tipo_de_archivo}')
        
         # Inicializar la lista de áreas y líneas
        lista_areas = []
        

        if tipo_de_plantilla == 'PLANTILLA':

            # Realizar la consulta si el nombre de la plantilla es 'PLANTILLA'
            plantillas = Plantilla.objects.filter(estado='HABILITADO').exclude(tipo_de_area=0).exclude(archivo = '').order_by('archivo')
            # Convertir los nombres de los archivos a un formato JSON
            documentos = [{'archivo': plantilla.archivo.name} for plantilla in plantillas]
            
            #print(documentos)

            # Devolver una respuesta JSON con los datos de los documentos
            return JsonResponse({'documentos': documentos})
        
    
        if tipo_de_archivo == '2':
            # Caso para el tipo de archivo '2'
            areas = Linea.objects.filter(area__area='Departamento').order_by('nombre_linea').distinct('nombre_linea')
            #CONTEXTO QUE ESTOY MANDANDO A MI TEMPLATE 'area' al json
            lista_areas = [{'area': area.nombre_linea,'id': area.area.id ,'codigo_linea': area.codigo_linea} for area in areas]
            #print(lista_areas) 
        elif tipo_de_archivo == '4':
            # Caso para el tipo de archivo '4', ajustar según la lógica necesaria
            areas = Linea.objects.exclude(area__area='Departamento').order_by('area__area').distinct('area__area')
            lista_areas = [{'area': area.area.area, 'id': area.area.id} for area in areas]
            #print(lista_areas)
        else:
            # Caso para otros tipos de archivo, ajustar según la lógica necesaria
            areas = Linea.objects.exclude(area__area='Departamento').order_by('area__area').distinct('area__area')
            lista_areas = [{'area': area.area.area, 'id': area.area.id} for area in areas]
            #print(lista_areas) 
        
        
        
        
     # Retorna ambos, el tipo de plantilla y las áreas en una sola respuesta
        return JsonResponse({'tipo_de_plantilla': tipo_de_plantilla, 'areas': lista_areas}, safe=False)
    except Plantilla.DoesNotExist as e:
        return JsonResponse({'error': 'La plantilla no existe'}, status=404)
    except Exception as e:  # Para capturar cualquier otra excepción que pudiera ocurrir
        return JsonResponse({'error': str(e)}, status=500)

def get_documents(tipo_de_archivo, linea):
    documents = Documento.objects.annotate(
        Nombre_documento=Concat(
            F('id_plantilla__codigo'), Value('-'),
            F('id_linea__codigo_linea'), Value(' '),
            Case(
                When(consecutivo='00', then=Value('00')),
                When(consecutivo__lt=10, then=Concat(Value('0'), F('consecutivo'))),
                default=F('consecutivo'),
                output_field=CharField()
            ),
               Value(' REV. '), F('revision_documento'), Value(' '), F('nombre'),
            output_field=CharField()
        )
    ).filter(
        estado='APROBADO',
        id_plantilla__nombre=tipo_de_archivo,
        id_linea__nombre_linea=linea
    ).order_by('Nombre_documento')

    return documents

def ajaxareas(request):
    # Filtra las líneas basándote en el área seleccionada
    area_seleccionadaxd = request.GET.get('areaSeleccionada')
    #print(f'EL area_seleccionada es: {area_seleccionadaxd}')

    
    lineas = Linea.objects.filter(area_id=area_seleccionadaxd).order_by('nombre_linea')

    # Construye una lista de diccionarios basada en las líneas filtradas
    lista_lineas = [{'linea': linea.nombre_linea, 'id': linea.id} for linea in lineas]
    #print(lista_lineas)
    
    return JsonResponse({'lineas': lista_lineas}, safe=False)



def ajax_linea(request):
    print("Se ejecuto el ajax linea")
    if request.method == 'GET':
         # Guardar IDs en la sesión
        print(request.GET)
        #print("SI ENTRE") 
        area =  request.GET.get('areaSeleccionada')
        plantilla =request.GET.get('plantillaSeleccionada')
        linea  = request.GET.get('lineaSeleccionada')
        

        
        documentos = get_documents(plantilla,linea)
        
        lista_documentos = [{'id': doc.id, 'documento': doc.Nombre_documento} for doc in documentos]


        # Enviar la lista de nombres de documentos como respuesta JSON
        return JsonResponse({'documentos': lista_documentos})
        
        

        
       
    return JsonResponse({'documentos': documentos}, safe=False)
     
