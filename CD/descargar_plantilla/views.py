from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from Documentos.forms import DocumentoForm, FormatosPermitidosForm,PlantillaForm
from Usuarios.forms import LineaForm,AreaForm
from Documentos.models import FormatosPermitidos,Documento,Plantilla,Historial,DocumentoBloqueado
from Usuarios.models import Linea,Area
import uuid
from django.conf import settings
import json
from Entrenamiento.models import Entrenamiento
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.core.files.base import ContentFile
from django.contrib import messages
from django.db import transaction
from django.db.models import F, Value , CharField,Func
from django.db.models.functions import Concat,Cast
from django.db.models.expressions import Case, When
from func.guardar_documento import GuardarDocumento
from func.clases_de_documento import nomenclatura_plantilla
import os
import re

# Create your views here.


#RENDERIZO EL FORMULARIO DE PLANTILLA
def descargar(request):
    template_name = 'documentos/descargar_plantilla.html'
    
    plantillas_habilitadas = Plantilla.objects.filter(estado='HABILITADO').order_by('nombre')
    areas_habilitadas = Area.objects.all().order_by('area')
    lineas_habilitadas = Linea.objects.all().order_by('nombre_linea')  
    
    plantila_form = PlantillaForm()
    area_form = AreaForm()
    linea_form = LineaForm()
    
    choices_plantillas =  [(plantilla.id, plantilla.nombre) for plantilla in plantillas_habilitadas]
    choices_areas =  [(area.id, area.area) for area in areas_habilitadas]
    choices_lineas =  [(linea.id, linea.nombre_linea) for linea in lineas_habilitadas]
    
    plantila_form.fields['nombre'].choices = choices_plantillas
    area_form.fields['area'].choices = choices_areas
    linea_form.fields['nombre_linea'].choices = choices_lineas

    contexto = {
        'plantila_form': plantila_form,
        'area_form': area_form,
        'linea_form': linea_form,
    }

    return render(request, template_name, contexto)



#obtener OBTENGO EL VALRO QUE SE REQUIERE DEPENDIENDO EL TIPO DE PLANTILAL QUE SE SELECCCIONA
def ajaxarchivo(request):
    tipo_de_plantilla = request.GET.get('nombre')
    area_seleccionada = request.GET.get('area')
    getid = Plantilla.objects.get(id = tipo_de_plantilla)
    nombre_plantilla = getid.nombre
    print(nombre_plantilla)
    
   
    try:
        plantilla = Plantilla.objects.get(nombre=nombre_plantilla)
        tipo_de_archivo = plantilla.tipo_de_area
        codigo_plantilla = plantilla.codigo
        print(f'tipo de archivo es:  {tipo_de_archivo}')
        
         # Inicializar la lista de áreas y líneas
        lista_areas = []
        

        if nombre_plantilla == 'PLANTILLA':

            # Realizar la consulta si el nombre de la plantilla es 'PLANTILLA'
            plantillas = Plantilla.objects.filter(estado='HABILITADO').exclude(tipo_de_area=0).exclude(archivo = '').order_by('archivo')
            # Convertir los nombres de los archivos a un formato JSON
            documentos = [{'archivo': plantilla.archivo.name} for plantilla in plantillas]
            
            print(documentos)

            # Devolver una respuesta JSON con los datos de los documentos
            return JsonResponse({'documentos': documentos})
        
    
        if tipo_de_archivo == '2':
            # Caso para el tipo de archivo '2'
            areas = Linea.objects.filter(area__area='Departamento').order_by('nombre_linea').distinct('nombre_linea')
            #CONTEXTO QUE ESTOY MANDANDO A MI TEMPLATE 'area' al json
            lista_areas = [{'area': area.nombre_linea,'id': area.area.id ,'codigo_linea': area.codigo_linea} for area in areas]
            print(lista_areas) 
        elif tipo_de_archivo == '4':
            # Caso para el tipo de archivo '4', ajustar según la lógica necesaria
            areas = Linea.objects.exclude(area__area='Departamento').order_by('area__area').distinct('area__area')
            lista_areas = [{'area': area.area.area, 'id': area.area.id} for area in areas]
            print(lista_areas)
        else:
            # Caso para otros tipos de archivo, ajustar según la lógica necesaria
            areas = Linea.objects.exclude(area__area='Departamento').order_by('area__area').distinct('area__area')
            lista_areas = [{'area': area.area.area, 'id': area.area.id} for area in areas]
            print(lista_areas) 
        
    
     # Retorna ambos, el tipo de plantilla y las áreas en una sola respuesta
        return JsonResponse({'tipo_de_plantilla': tipo_de_plantilla, 'areas': lista_areas}, safe=False)
    except Plantilla.DoesNotExist as e:
        return JsonResponse({'error': 'La plantilla no existe'}, status=404)
    except Exception as e:  # Para capturar cualquier otra excepción que pudiera ocurrir
        return JsonResponse({'error': str(e)}, status=500)


#Este ajax se obtiene el area para filtrar las lineas correspondientes
def ajaxareas(request):
    # Filtra las líneas basándote en el área seleccionada
    area_seleccionadaxd = request.GET.get('areaSeleccionada')
    print(f'EL area_seleccionada es: {area_seleccionadaxd}')

    lineas = Linea.objects.filter(area_id=area_seleccionadaxd).order_by('nombre_linea')

    # Construye una lista de diccionarios basada en las líneas filtradas
    lista_lineas = [{'linea': linea.nombre_linea, 'id': linea.id} for linea in lineas]
    #print(lista_lineas)
    
    return JsonResponse({'lineas': lista_lineas}, safe=False)



#Este ajax se tiene al seleciona la linea en caso que exista un documento que fitre los documentos correspondientes
def ajax_linea(request):
    print("Se ejecuto el ajax linea")
    if request.method == 'GET':
        # Guardar IDs en la sesión
        request.session['linea_id'] = request.GET.get('lineaSeleccionada')
        request.session['plantilla_id'] = request.GET.get('plantillaSeleccionada')
        request.session['area_id'] = request.GET.get('areaSeleccionada')
        
        # Recuperar y almacenar los nombres basados en los IDs
        try:
            linea = Linea.objects.get(id=request.session['linea_id'])
            plantilla = Plantilla.objects.get(id=request.session['plantilla_id'])
            area = Area.objects.get(id=request.session['area_id'])

            # Guardar nombres en la sesión
            request.session['linea_seleccionada'] = linea.nombre_linea
            request.session['plantilla_seleccionada'] = plantilla.nombre
            request.session['area_seleccionada'] = area.area

            print(f"La línea es {request.session['linea_seleccionada']}, la plantilla es {request.session['plantilla_seleccionada']}, el área es {request.session['area_seleccionada']}")

            documentos = Documento.objects.filter(
            estado='APROBADO',
            id_plantilla__nombre=plantilla.nombre,
            id_linea__nombre_linea=linea.nombre_linea
        ).annotate(
            consecutivo_str=Case(
                When(consecutivo=0, then=Value('00')),
                When(consecutivo__lt=10, then=Concat(Value('0'), F('consecutivo'))),
                default=F('consecutivo'),
                output_field=CharField()
            )
        ).annotate(
            nombre_anotacion=Concat(
                F('id_plantilla__codigo'), Value('-'), F('id_linea__codigo_linea'), Value(' '),
                'consecutivo_str', Value(' REV. '), F('revision_documento'), Value(' '), F('nombre'),
                output_field=CharField()
            )
        ).order_by('nombre')

            documentos_list = [documento.nombre_anotacion for documento in documentos]
            print(documentos_list)

            return JsonResponse({'documentos': documentos_list}, status=200)
        except ObjectDoesNotExist:
            return JsonResponse({'error': 'Uno o más elementos no existen'}, status=404)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)
        

    
    
#Esta  funcion hace algo en especifco cuando es de crear documento cuandp ose activa
def ajax_checkbox(request):
    if request.method == "GET":
        plantilla_seleccionada = request.GET.get('nombrePlantillaSeleccionada')
        area_seleccionada = request.GET.get('areaSeleccionada')
        linea_seleccionada = request.GET.get('lineaSeleccionada')
    #data = json.loads(request.body)
    
    #nombre_plantilla = data.get('nombrePlantillaSeleccionada')
    
    plantillas = Plantilla.objects.get(id=plantilla_seleccionada)
    nombre_plantilla= plantillas.nombre
    
    lineas = Linea.objects.get(id=linea_seleccionada)
    nombre_linea= lineas.nombre_linea
    
    print(f'soy global plantilla {nombre_plantilla}')
    print(f'soy global Linea {nombre_linea}')
    print(f'soy global Area {area_seleccionada}')    

    linea_disabled = request.GET.get('lineaDisabled', False) == 'true'
    print(linea_disabled)



    documentos_data = []


    if not linea_disabled:
        print("ENTRE AL METODO")
        documentos = Documento.objects.filter(
            estado='APROBADO',
            id_plantilla__nombre=nombre_plantilla,
            id_linea__nombre_linea=nombre_linea
        ).annotate(
            consecutivo_str = Case(
            When(consecutivo__lt=10, then=Concat(Value('0'), Cast('consecutivo', output_field=CharField()))),
            default=F('consecutivo'),
            output_field=CharField()
        )
        ).annotate(
            nombre_anotacion=Concat(
                F('id_plantilla__codigo'), Value('-'), F('id_linea__codigo_linea'), Value(' '),
                'consecutivo', Value(' REV. '), F('revision_documento'), Value(' '), F('nombre'),
                output_field=CharField()
            )
        ).order_by('nombre')
        
        
        if documentos:
            for documento in documentos:
                nombre_documento = f"{documento.id_plantilla.codigo}-{documento.id_linea.codigo_linea} "
                nombre_documento += f"{documento.consecutivo} REV. {documento.revision_documento} {documento.nombre}"
                print('nombre de documento', nombre_documento)
                documentos_data.append(nombre_documento)
            print('docuemntos . data ' ,documentos_data)
            return JsonResponse({'documentos': documentos_data})  
        else:
            return JsonResponse({"sucees":'Documento no encontrado'})

    else:
        documentos = Documento.objects.filter(
            estado='APROBADO',
            id_plantilla__nombre=nombre_plantilla,
            id_linea__nombre_linea=nombre_linea
        ).annotate(
            consecutivo_str = Case(
            When(consecutivo__lt=10, then=Concat(Value('0'), Cast('consecutivo', output_field=CharField()))),
            default=F('consecutivo'),
            output_field=CharField()
        )
        ).annotate(
            nombre_documento =Concat(
                F('id_plantilla__codigo'), Value('-'), F('id_linea__codigo_linea'), Value(' '),
                'consecutivo', Value(' REV.'), F('revision_documento'), Value(' '), F('nombre'),
                output_field=CharField()
            )
        ).order_by('nombre')
        
        for documento in documentos:
            nombre_documento = f"{documento.id_plantilla.codigo}-{documento.id_linea.codigo_linea} "
            nombre_documento += f"{documento.consecutivo} REV. {documento.revision_documento} {documento.nombre}"
            documentos_data.append(nombre_documento)

    return JsonResponse({'documentos': documentos_data})



#Este va hacer un ajax para restricciones y determina la revision
def ajaxdetermine_revision(request):
    if request.method == "GET":
        plantilla_seleccionada = request.session.get('plantilla_seleccionada')
        area_seleccionada = request.session.get('area_seleccionada')
        linea_seleccionada = request.session.get('linea_seleccionada')
        checkbox_value = request.GET.get('cb_Nuevo') == 'true'
        document_name = request.GET.get('nombreDocumento', '')
        documento_query = None  # Inicializar con None

        print(request.GET)
        
        # Lógica del checkbox
        revision = "00" if checkbox_value else ''

        if not checkbox_value:
            # Obtiene el último número de revisión a partir de la base de datos
            try:
                top_rev_documento = Documento.objects.filter(
                    estado='APROBADO',
                    id_plantilla__codigo=F('codigo_linea') + '-' + F('id_linea__codigo_linea') + ' ' +
                    Case(
                        When(consecutivo__lt=10, then=Concat(Value('0'), 'consecutivo')),
                        default='consecutivo'
                    ) + ' REV. ' + F('revision_documento') + ' ' + F('nombre')
                ).order_by('-id').values_list('revision_documento', flat=True).first()
                
                if top_rev_documento:
                    next_revision = int(top_rev_documento) + 1
                    revision = f"{next_revision:02d}"
                else:
                    return JsonResponse({"error": "Este documento no cuenta con ninguna revisión previa"}, status=400)
            except Documento.DoesNotExist:
                return JsonResponse({"error": "Documento no encontrado"}, status=404)

        # Proceso para determinar el consecutivo nuevo
        tipo_archivo_query = Plantilla.objects.get(nombre=plantilla_seleccionada)
        linea_query = Linea.objects.get(nombre_linea=linea_seleccionada)

        if tipo_archivo_query.tipo_de_area in ["2", "4"]:
            documento_query = Documento.objects.filter(
                id_linea=linea_query,
                id_plantilla=tipo_archivo_query,
                estado='APROBADO'
            ).order_by('-consecutivo').first()

        if documento_query:
            consecutivo_nuevo = int(documento_query.consecutivo) + 1
            consecutivo_nuevo_str = f'{consecutivo_nuevo:02d}'
        else:
            consecutivo_nuevo_str = "01"

        if checkbox_value:
            return JsonResponse({
                "document_name": f"{tipo_archivo_query.codigo}-{linea_query.codigo_linea} {consecutivo_nuevo_str} REV. {revision} {document_name}"
            })
        else:
            nombre_documento = document_name.split(' ')
            return JsonResponse({
                "document_name": f"{nombre_documento[0]} REV.{revision} {' '.join(nombre_documento[1:])}"
            })

    return JsonResponse({"revision": revision})


#Aqui se inserta el numero de intentatos al selccionar el documento
#y verifica si el usuario ya esta siendo editado por alguein mas si esta blqoueado el documento 
def nombre_doc_SelectedIndexChanged(request):

    if request.method == "POST":
        # Extraer el nombre del documento de los datos POST enviados con el formulario o solicitud AJAX
        nombre_documento = request.POST.get('nombreDocumento', None)
        nombrePlantillaSeleccionada = request.POST.get('nombrePlantillaSeleccionada')
        isChecked = request.POST.get('isChecked')
        pllantilla_cheked = request.POST.get('plantilla_completa')
        linea_seleccionada = request.POST.get('lineaSeleccionada')


        plantillas = Plantilla.objects.get(id=nombrePlantillaSeleccionada)
        nombre_plantilla = plantillas.nombre
        codigo_Docum = plantillas.codigo
        revision_Actual = plantillas.revision_actual
        ruta_docum = plantillas.archivo
        
        lineas = Linea.objects.get(id = linea_seleccionada)
        codigo_linea = lineas.codigo_linea
        
        nomenclatura = None
        
        
        if nombre_plantilla == 'PLANTILLA':
            nombre_archivo = os.path.basename(nombre_documento)
            print("El nombre asignado es: " , nombre_archivo) 
        
            # Separar las partes del nombre del documento
            nombre_parts = nombre_archivo.split('_')
            print("Partes del nombre:", nombre_parts)

            # Extraer el número de documento y línea de la primera parte
            partes_iniciales = nombre_parts[0].split('-')
            no_documento = partes_iniciales[0]
            no_linea = partes_iniciales[1]

            # El consecutivo parece ser el segundo elemento de nombre_parts
            consecutivo = nombre_parts[1]
            
            nomenclatura = f'{no_documento}-{no_linea} {consecutivo}'
            print("nombre temporal de verificacion: ", nomenclatura)
        
        if isChecked == 'true':
            nomenclatura = f'{codigo_Docum}-{codigo_linea} {revision_Actual}'
            print("nombre temporal de verificacion: ", nomenclatura)
        else:
              nombre_parts = nombre_documento.split(' ')
                    # Verificar si hay suficientes partes en el nombre del documento
              if len(nombre_parts) >= 2:
                # Combinar el número de documento y el número de línea en una sola cadena
                nomenclatura = f"{nombre_parts[0]} {nombre_parts[1]}"
                print("nombre temporal de verificacion: ", nomenclatura)
            
             
        documento_bloqueado = DocumentoBloqueado.objects.filter(
            nomenclatura=nomenclatura,
            id_responsable__perfilusuario__estado='ACTIVO'
        ).first()

        if documento_bloqueado is not None:
            usuario_editando = documento_bloqueado.id_responsable
            full_name = usuario_editando.get_full_name()
            mensaje = f"Este documento está siendo editado por el usuario '{full_name}', por lo que no se puede descargar en este momento. Le sugerimos contactarse con el usuario para proponer sus cambios o con el administrador para desbloquear el documento."
            documento_bloqueado.intentos_descarga += 1 # suma +1 en la base de datos pro cada intentor de descarga
            documento_bloqueado.save()

            return JsonResponse({'message': mensaje})
        
         
        # Aquí deberías agregar la lógica de descarga si no está bloqueado
        return JsonResponse({'success': 'Documento no está bloqueado, proceda con la descarga'})
          
            
    # Si el método no es POST o no se encuentra ningún documento bloqueado, devolver un mensaje de éxito
    return JsonResponse({'success': 'Operación realizada correctamente'})
        
    
#verificar a fondo el de descargar   
#Metodo donde se realiza la descagar del documento dependiente la situacion  del tipo de documento que se descarge y aumenta la revision 
def cD_Boton1_Click(request):
    if request.method == "POST":
        isChecked = request.POST.get('isChecked')
        nombrePlantillaSeleccionada = request.POST.get('nombrePlantillaSeleccionada')
        lineaSeleccionada = request.POST.get('lineaSeleccionada')
        nombreDocumento = request.POST.get('nombreDocumento')
        
        area_seleccionada = request.session.get('area_seleccionada')
        nombre_del_documento = ''
        revision = '00' if isChecked == 'true' else ''
        consecutivo_nuevo = None
        
        def get_plantilla(nombrePlantillaSeleccionada):
            try:
                plantilla = Plantilla.objects.get(id=nombrePlantillaSeleccionada)
                return plantilla.nombre, plantilla.codigo, plantilla.archivo
            except Plantilla.DoesNotExist:
                return None, None, None
            except Exception as e:
                return str(e), None, None

        def get_linea(lineaSeleccionada):
            try:
                linea = Linea.objects.get(id=lineaSeleccionada)
                return linea.nombre_linea, linea.codigo_linea
            except Linea.DoesNotExist:
                return None, None
            except Exception as e:
                return str(e), None
        
        nombre_plantilla, codigo_Docum, ruta_docum = get_plantilla(nombrePlantillaSeleccionada)
        
        
        if not nombre_plantilla:
            return JsonResponse({'error': 'Plantilla no encontrada'}, status=404)
        elif isinstance(nombre_plantilla, str) and not codigo_Docum:
            return JsonResponse({'error': f'Error al obtener la plantilla: {nombre_plantilla}'}, status=500)
        
        nombre_linea, codigo_linea = get_linea(lineaSeleccionada)
        if not nombre_linea:
            return JsonResponse({'error': 'Línea no encontrada'}, status=404)
        elif isinstance(nombre_linea, str) and not codigo_linea:
            return JsonResponse({'error': f'Error al obtener la línea: {nombre_linea}'}, status=500)

        print(f"isChecked: {isChecked}, nombrePlantillaSeleccionada: {nombrePlantillaSeleccionada}, lineaSeleccionada: {lineaSeleccionada}, nombreDocumento: {nombreDocumento}")

        if nombre_plantilla == "PLANTILLA":
            print("Entre al metodo Plantilla")
            nombre_archivo = os.path.basename(nombreDocumento)
            nombre_parts = nombre_archivo.split('_')
            print(nombre_parts)
            if len(nombre_parts) >= 3:
                revision_actual_part = nombre_parts[2]
                revision_actual = revision_actual_part.split('.')[1]
                try:
                    nueva_revision = str(int(revision_actual) + 1).zfill(2)
                    consecutivo_nuevo = nueva_revision
                 
                    no_documento, no_linea, consecutivo, revision, nombre_doc = nomenclatura_plantilla(nombre_archivo)
                    
                    nomenclatura = f'{no_documento}-{no_linea} {consecutivo_nuevo}'
                    
                    nombre_del_documento = f'{no_documento}-{no_linea} {consecutivo} REV. {consecutivo_nuevo} {nombre_doc}.docx'
                    nombre_del_documento_sin_ext = f'{no_documento}-{no_linea} {consecutivo} REV. {consecutivo_nuevo} {nombre_doc}'

                                        
                    
                    print("nombrel de documento: " , nombre_del_documento)
                    print("nomenclatura  es: ", nomenclatura)
                    print("ruta del documento: ", ruta_docum)

                    #Metodo para insertar en la abse de datos 
                    insertdoc_block(nomenclatura,request.user,nombre_del_documento_sin_ext)

                    #Manda  al mentodo para la descargar del archivo 
                    response = copy_file_and_provide_download_url(request, nombreDocumento, nombre_del_documento)
                    return response
                
                except ValueError:
                    return JsonResponse({'error': 'La revisión actual no es un número válido'}, status=400)

        if isChecked == 'true':
            print("si entre al cheked")
            last_consecutivo = Documento.objects.exclude(estado='RECHAZADO').filter(
                id_linea__area__area=Area,
                id_plantilla__nombre=nombre_plantilla
            ).order_by('-consecutivo').first()

            consecutivo_nuevo = "{:02d}".format(int(last_consecutivo.consecutivo) + 1) if last_consecutivo else "01"
            nombre = f'{codigo_Docum}-{codigo_linea} {consecutivo_nuevo} REV. {revision} {nombreDocumento}'
            nombre_del_documento = nombre.rstrip('.docx')
            
            nombre_temp = f"{codigo_Docum}-{codigo_linea} {consecutivo_nuevo}"

            
            insertdoc_block(nombre_temp,request.user,nombre_del_documento)
            
            
            response = copy_file_and_provide_download_url(request, ruta_docum, nombre_del_documento)
            
            return response
        else:
            print("Entre al metodo actulizar documento")
            print("nombre_documentoo" , nombreDocumento)
            documento = Documento.objects.annotate(
            nombre_completo=Concat(
                F('id_plantilla__codigo'), Value('-'),
                F('id_linea__codigo_linea'), Value(' '),
                Case(
                    When(consecutivo__lt=10, then=Concat(Value('0'), Cast('consecutivo', output_field=CharField()))),
                    default=Cast('consecutivo', output_field=CharField()),
                    output_field=CharField()
                ),
                Value(' REV. '), F('revision_documento'), Value(' '), F('nombre')
            )
        ).filter(
            nombre_completo=nombreDocumento,
            estado='APROBADO'
)

            if documento:
                print("si entre al if documento")
                id_documento = documento[0].id
                revision_plantilla = int(documento[0].revision_de_plantilla)  # Asegúrate de que es entero
                
                print("tipo de plantilla" , nombre_plantilla)
                
                plantilla = Plantilla.objects.filter(nombre=nombre_plantilla).first()

                revision_actual = int(plantilla.revision_actual)  # Asegúrate de que es entero
                
                
                print('id_documento',id_documento,'revison actual: ', revision_actual , 'revision_plantilla: ', revision_plantilla)
                if revision_plantilla == revision_actual:
                    print("si se cumplio")
                    # Crea una instancia de GuardarDocumento primero
                    guardar_documento = GuardarDocumento(settings.RUTA_EDITABLES_DOCUMENTOS)

                    # Luego llama al método get_ruta
                    ruta_archivo = guardar_documento.get_ruta(id_documento)

    
                
                print("no se cumplio")
                nombre_parts = nombreDocumento.split(' ')
                revision_part_index = None
                for i, part in enumerate(nombre_parts):
                    if "REV." in part:
                        revision_part_index = i
                        break

                if revision_part_index is not None and (revision_part_index + 1) < len(nombre_parts):
                    revision_number_part = nombre_parts[revision_part_index + 1]
                    if revision_number_part.isdigit():
                        nueva_revision = str(int(revision_number_part) + 1).zfill(2)
                        nombre_parts[revision_part_index + 1] = nueva_revision
                        nuevo_nombre = ' '.join(nombre_parts)
                        nombre_del_documento = nuevo_nombre
                        
                        nombre_temp = f"{codigo_Docum}-{codigo_linea} {nueva_revision}"

                        insertdoc_block(nombre_temp,request.user,nombre_del_documento)

                    
                        response = copy_file_and_provide_download_url(request, ruta_docum, nuevo_nombre)
                        return response
                    else:
                        return JsonResponse({'error': 'La parte de revisión no es un número válido'}, status=400)
                else:
                    return JsonResponse({'error': 'No se encontró la parte "REV." o está mal formateada en el nombre del documento.'}, status=400)
                
                
                
    return JsonResponse({'success': 'Operación realizada correctamente'})


#Metodo no se inserta el documento para que se bloqueee
def insertdoc_block(nombre_temp,usuario_actual,nombre_del_documento):
    doc_bloqueado = DocumentoBloqueado.objects.create(
            nomenclatura=nombre_temp,
            id_responsable=usuario_actual,
            estado='En edición',
            codigo_identificacion=f"{uuid.uuid4().hex[:7]}-{nombre_del_documento}",
        )
    doc_bloqueado.save()
    print("Se inserto correctamente")
        
        
    
    
        



    

def copy_file_and_provide_download_url(request, original_url, new_name):
    # Asegúrate de que original_url es una cadena con la ruta del archivo
    if isinstance(original_url, str):
        path = original_url
    elif hasattr(original_url, 'path'):
        path = original_url.path  # Usa .path para obtener la ruta completa al archivo
    else:
        return JsonResponse({'error': 'Invalid file path or object'})

    print("Ruta original:", path)

    # Verificar si el archivo original existe
    if default_storage.exists(path):
        content = default_storage.open(path).read()
        
        # Asegurarse de no duplicar la extensión .docx
        if not new_name.endswith('.docx'):
            new_name += '.docx'

        new_file_name = new_name
        new_file_path = os.path.join('temp', new_file_name)  # Almacenar en subdirectorio 'temp' bajo 'media'

        # Guardar el nuevo archivo en la carpeta temporal
        default_storage.save(new_file_path, ContentFile(content))

        new_url = request.build_absolute_uri(f'/media/temp/{new_file_name}')
        return JsonResponse({'new_file_url': new_url,'new_file_name' :new_file_name })
    else:
        error_msg = f"Archivo no encontrado en la ruta: {path}"
        print(error_msg)
        return JsonResponse({'error': 'File not found', 'message': error_msg})


    
    
    
    