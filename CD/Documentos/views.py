from django.shortcuts import render, redirect
from .forms import DocumentoForm, FormatosPermitidosForm
from .models import FormatosPermitidos,Documento,Plantilla,Historial,DocumentoBloqueado
from Usuarios.models import Linea
from Entrenamiento.models import Entrenamiento
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.core.files.base import ContentFile
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.db.models import F, Value, CharField
from django.db.models.functions import Concat, Cast
from django.db.models.expressions import Case, When
import os



#Agregar Documento


#Metodo para agregar un documento en la base de datos 
def adddoc(request):
    template_name = 'documentos/agregar_documento.html'
    
    extensiones_permitidas = [ext[0] for ext in FormatosPermitidos.extension_documentos_choices]

    if request.method == 'POST':
        documento_form = DocumentoForm(request.POST, request.FILES)
        
        if documento_form.is_valid():
            id_linea = documento_form.cleaned_data.get('id_linea').id
            id_plantilla = documento_form.cleaned_data.get('id_plantilla').id
            consecutivo_str = documento_form.cleaned_data.get('consecutivo')  # Mantener el valor como cadena para rutas
            consecutivo = int(consecutivo_str)  # Convertir a entero para validaciones
            revision = documento_form.cleaned_data.get('revision_documento')
            revision_plantilla = int(documento_form.cleaned_data.get('revision_de_plantilla'))  # Convertir a entero

            lineas = Linea.objects.get(id=id_linea)
            codigo_linea = lineas.codigo_linea
            nombre_linea = lineas.nombre_linea
            
            if verificar_consecutivo(id_linea, id_plantilla, consecutivo):
                try:
                    with transaction.atomic():
                        documento = documento_form.save(commit=False)
                        plantilla_seleccionada = documento_form.cleaned_data['id_plantilla']
                        plantilla_nombre = plantilla_seleccionada.nombre
                        plantilla_codigo = plantilla_seleccionada.codigo
                        nombre_documento = documento_form.cleaned_data['nombre'] 
                        
                        rutadoc = f'{plantilla_nombre}/{nombre_linea}/{plantilla_codigo}-{codigo_linea} {consecutivo_str} REV. {revision} {nombre_documento}.docx'
                        rutapdf = f'{plantilla_nombre}/{nombre_linea}/{plantilla_codigo}-{codigo_linea} {consecutivo_str} REV. {revision} {nombre_documento}.pdf'

                        editable_file = request.FILES['editable_document']
                        editable_file_path = f'Control_de_documentos_Editables/{rutadoc}'
                        default_storage.save(editable_file_path, ContentFile(editable_file.read()))
                        
                        pdf_file = request.FILES['pdf_document']
                        pdf_file_path = f'Control_de_documentos_pdfs/{rutapdf}'
                        default_storage.save(pdf_file_path, ContentFile(pdf_file.read()))
                        
                        documento.nombre = nombre_documento  + '.docx' # Asegúrate de que 'nombre_archivo' es el campo correcto en tu modelo Documento
                        documento.consecutivo = int(consecutivo)
                        documento.revision_de_plantilla = int(revision_plantilla)
                        documento.comentarios = 'Documento dado de alta manualmente'

                        print("inserte este nombre: ",f'{ nombre_documento}.docx')
                        documento.save()
                        
                        messages.success(request, 'Los datos se han guardado correctamente.')
                        return redirect('home')
                except ObjectDoesNotExist as e:
                    messages.error(request, f'Error: El objeto no existe - {e}')
                except ValidationError as e:
                    messages.error(request, f'Error de validación: {e.message_dict}')
                except Exception as e:
                    messages.error(request, f'Error inesperado: {e}')
            else:
                messages.error(request, "El consecutivo asignado a este documento ya está ocupado y no es posible duplicarlo.")
        else:
            error_message = ". ".join([f"{campo}: {','.join(errors)}" for campo, errors in documento_form.errors.items()])
            messages.error(request, f'Por favor, revisa los campos: {error_message}')
    else:
        documento_form = DocumentoForm()

    context = {
        'documento_form': documento_form,
        'extensiones_permitidas': extensiones_permitidas,
    }
    return render(request, template_name, context)





#CONSULTA ORM DE SQL PARA SABER EL CONSECUTIVO
def verificar_consecutivo(id_linea, id_plantilla, consecutivo):
    documentos = Documento.objects.filter(
        id_linea=id_linea, 
        id_plantilla=id_plantilla, 
        consecutivo=consecutivo
    ).exclude(estado__in=['RECHAZADO', 'OBSOLETO'])
    return not documentos.exists()


#SECCION PARA DESCARGAR PLNATILLA

#Query para  documentos con su codigo de plantilla
def documentosquery():
    documentos = Documento.objects.filter(
        estado='APROBADO'
    ).select_related(
        'id_plantilla', 'id_linea'
    ).annotate(
        codigo_concat=Concat(
            F('id_plantilla__codigo'), Value('-'),
            F('id_linea__codigo_linea'), Value(' '),
            Case(
                When(consecutivo='00', then=Value('00')),
                When(consecutivo__lt=10, then=Concat(Value('0'), Cast('consecutivo', output_field=CharField()))),
                default=Cast('consecutivo', output_field=CharField()),
            ),
            Value(' REV.'), F('revision_documento'), Value(' '), F('nombre'),
            output_field=CharField()
        )
    )
    
    Id_Documento = 1
    
   
    historial_query = Historial.objects.filter(
        id_documento_id=Id_Documento
    ).annotate(
        nombre_completo=Concat(
            F('id_responsable__first_name'), Value(' '), 
            F('id_responsable__last_name'), 
            output_field=CharField()
        )
    ).values(
        'nombre_completo', 'fecha', 'accion'
    )
    
    
    entrenamientos_query = Entrenamiento.objects.filter(
        id_documento_id=Id_Documento
    ).annotate(
        nombre_completo=Concat(
            F('id_usuario__first_name'), Value(' '), 
            F('id_usuario__last_name'), 
            output_field=CharField()
        )
    ).values(
        'nombre_completo', 'calificacion', 'fecha'
    )
    


    for documento in documentos:
        print(documento.codigo_concat) 
        
        








