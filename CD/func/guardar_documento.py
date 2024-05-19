from django.db.models import F, Value, Case, When, CharField
from django.db.models.functions import Concat,Cast
from django.shortcuts import get_object_or_404
from Documentos.models  import Documento,Linea,Plantilla
from func.clases_de_documento import get_ruta_actual,nomenclatura
from django.conf import settings
from func.firmar_documento import  FirmarDocumentos 
from func.inserta_sellos import insertar_referencia_imagen,quitar_sellos
import subprocess
import os
from  func.clases_de_documento import get_ruta_obsoleta,get_ruta_actual


class GuardarDocumento:
    def __init__(self, ruta_principal):
        self.ruta_principal = ruta_principal


    def get_ruta(self,id_archivo):
        try:
            documento = Documento.objects.select_related('id_plantilla', 'id_linea', 'id_linea__area').get(pk=id_archivo)

            nombre_documento = documento.nombre
            area = documento.id_linea.area.area
            linea = documento.id_linea.nombre_linea

            # Tu segundo SQL que genera la ruta completa
            ruta = Plantilla.objects.filter(id_plantilla=documento.id_plantilla_id).annotate(
                ruta_completa=Concat(
                    Value(self.ruta_principal),  # Asumiendo que RutaPrincipal es una variable definida en algún lugar en tu código.
                    Value('\\'),
                    Case(
                        When(tipo_de_area='1', then=Concat(
                            Case(
                                When(nombre__in=['Ayuda visual (Vertical)', 'Ayuda visual (Horizontal)'], then=Value('Ayuda visual')),
                                When(nombre__in=['Instrucciones de Operaciones (de proceso)', 'Instrucciones de Operaciones (de sistema)'], then=Value('Instrucciones de Operaciones')),
                                default=F('nombre')
                            ),
                            Value('\\Clientes\\'),
                            F('id_linea__area__area'),
                            Value('\\'),
                            F('id_linea__nombre_linea'),
                            Value('\\')
                        )),
                        When(id_linea__area__area='Departamento', then=Concat(
                            F('nombre'),
                            Value('\\'),
                            F('id_linea__nombre_linea'),
                            Value('\\')
                        )),
                        default=Value('Plantillas\\')
                    ),
                    Concat(
                        F('codigo'),
                        Value('-'),
                        F('id_linea__codigo_linea'),
                        Value(' '),
                        Cast('documento.consecutivo', output_field=CharField()),
                        Value(' REV.'),
                        F('documento.revision_documento'),
                        Value(' '),
                        F('nombre')
                    )
                )
            ).first().ruta_completa

            return ruta
        except Documento.DoesNotExist:
            # Implementa tu lógica si el documento no se encuentra
            print("No se encontró el documento con ID: {}".format(id_archivo))


    def guardar_documento(self,id_documento, ruta_archivo, documento, area, linea, nombre, tipo_documento):
        documento_instance = get_object_or_404(Documento, pk=id_documento)

        # Obtener las rutas de guardado de los archivos
        ruta_guardar_word = settings.RUTA_EDITABLES + get_ruta_actual(id_documento)
        ruta_guardar_pdf = ruta_guardar_word.replace('.docx', '.pdf')

        # Obtener nomenclatura del documento
        no_documento, no_linea, consecutivo, rev, nombre_del_documento = nomenclatura(documento_instance.nombre)

        # Convertir de Word a PDF y firmar el documento
        FirmarDocumentos.convert_word_to_pdf(ruta_archivo, ruta_guardar_pdf)
        quitar_sellos(ruta_archivo)

        # Procesar versiones obsoletas si la revisión no es '00'
        if rev != "00":
            ruta_actual_obsoleta_word, ruta_guardar_obsoleta_word = get_ruta_obsoleta(id_documento)
    
            ruta_word_actual_obsoleta = settings.RUTA_EDITABLES + ruta_actual_obsoleta_word
            ruta_word_proximo_obsoleta = settings.RUTA_EDITABLES + ruta_guardar_obsoleta_word

            ruta_guardar_obsoleta_pdf = ruta_word_proximo_obsoleta.replace('.docx', '.pdf')
            ruta_actual_obsoleta_pdf = ruta_word_actual_obsoleta.replace('.docx', '.pdf')

            # Agregar marca de agua a la versión obsoleta del PDF
            self.agregar_marca_agua_pdf(ruta_actual_obsoleta_pdf, ruta_guardar_obsoleta_pdf, "DOCUMENTO OBSOLETO")

            # Marcar documento anterior como obsoleto en la base de datos
            self.mover_obsoletos(nombre)

    def agregar_marca_agua_pdf(self,input_pdf_path, output_pdf_name, watermark_text):
        output_dir = settings.TEMP_OUTPUT_DIR

        # Check if the output directory exists, create if it doesn't
        os.makedirs(output_dir, exist_ok=True)

        # Path to the temporary watermark file
        watermark_file = os.path.join(output_dir, "watermark.pdf")

        # Generate a watermark PDF with diagonal centered text
        subprocess.run([
            'gs', '-o', watermark_file, '-sDEVICE=pdfwrite',
            '-c', "/Helvetica-Bold findfont 120 scalefont setfont",  # Set font size
            '-c', "1 0.82 0.86 setrgbcolor",  # Set text color
            '-c', "297.5 421 translate",  # Center origin at half an A4 page
            '-c', "45 rotate",  # Rotate text by 45 degrees
            '-c', "-350 -50 moveto",  # Adjust to center the rotated text
            '-c', f"({watermark_text}) show"
        ], check=True)

        # Construct the final PDF path with watermark
        watermarked_pdf_path = os.path.join(output_dir, f"OBSOLETO_{output_pdf_name}")
        subprocess.run([
            'pdftk', input_pdf_path, 'background', watermark_file, 'output', watermarked_pdf_path
        ], check=True)

        # Optionally, remove the original PDF if it's no longer needed
        os.remove(input_pdf_path)

        # Clean up watermark file
        os.remove(watermark_file)

        return watermarked_pdf_path

    def mover_obsoletos(self,nombre_documento):
        Documento.objects.filter(nombre=nombre_documento, estado='APROBADO').update(estado='OBSOLETO')

        

     
     
     
     
     


     
     
     
     
     
    