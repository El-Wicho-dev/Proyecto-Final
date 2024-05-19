import os
from django.contrib import messages
from docx import Document
from openpyxl import load_workbook
from pptx import Presentation
from Documentos.models import Documento,Plantilla
from Usuarios.models import Linea
from Entrenamiento.models import Firma
from django.db.models.functions import Concat,Cast
from django.db.models import F, Value , CharField,Func
from django.db.models.expressions import Case, When

from django.http import JsonResponse

class FirmarDocumentos:
    def __init__(self, path_pdf, path_edit):
        self.path_pdf = path_pdf
        self.path_edit = path_edit

    def guardar_pdf(self, nombre_archivo_r):
        nombre_archivo = nombre_archivo_r

        if nombre_archivo.endswith(".docx"):
            nombre_archivo = nombre_archivo.replace(".docx", ".pdf")
            self.convert_word_to_pdf(os.path.join(self.path_edit, nombre_archivo_r), os.path.join(self.path_pdf, nombre_archivo))
        elif nombre_archivo.endswith(".xlsx"):
            nombre_archivo = nombre_archivo.replace(".xlsx", ".pdf")
            self.convert_excel_to_pdf(os.path.join(self.path_edit, nombre_archivo_r), os.path.join(self.path_pdf, nombre_archivo))
        elif nombre_archivo.endswith(".pptx"):
            nombre_archivo = nombre_archivo.replace(".pptx", ".pdf")
            self.convert_powerpoint_to_pdf(os.path.join(self.path_edit, nombre_archivo_r), os.path.join(self.path_pdf, nombre_archivo))
        else:
            return JsonResponse({'mensaje': 'La extensión del archivo no es compatible.'})

        return JsonResponse({'mensaje': 'El archivo se ha guardado como PDF.'})

    def convert_word_to_pdf(self, input_file, output_file):
        try:
            doc = Document(input_file)
            doc.save(output_file)
            return True
        except Exception as e:
            print(f"Error al convertir Word a PDF: {e}")
            return False

    def convert_excel_to_pdf(self, input_file, output_file):
        try:
            wb = load_workbook(input_file)
            wb.save(output_file)
            return True
        except Exception as e:
            print(f"Error al convertir Excel a PDF: {e}")
            return False

    def convert_powerpoint_to_pdf(self, input_file, output_file):
        try:
            prs = Presentation(input_file)
            prs.save(output_file)
            return True
        except Exception as e:
            print(f"Error al convertir PowerPoint a PDF: {e}")
            return False
        
    def firmarWord_Ordinario(self,id_documento):
        try:
            nombre_documento = Documento.objects.filter(id_documento=id_documento).values(
                'id_plantilla__codigo',
                'id_linea__codigo',
                'consecutivo',
                'revision_documento',
                'nombre'
            ).annotate(
                nombre_completo=Concat(
                    'id_plantilla__codigo',
                    '-',
                    'id_linea__codigo',
                    'consecutivo',
                    'revision_documento',
                    'nombre',
                    output_field=CharField()
                )
            ).first()['nombre_completo']
        
            return nombre_documento
        except Documento.DoesNotExist:
            return None
        
    

    def firmar_documento(self,id_documento):
        try:
            nombre_documento = self.firmarWord_Ordinario(id_documento)
            if nombre_documento:
                responsable = Documento.objects.get(id_documento=id_documento).id_responsable
                revisador = Documento.objects.get(id_documento=id_documento).revisador
                aprobador = Documento.objects.get(id_documento=id_documento).aprobador
                id_firma_responsable = Firma.objects.filter(id_documento=id_documento, id_liberador=responsable).first().id_firma
                id_firma_revisador = Firma.objects.filter(id_documento=id_documento, id_liberador=revisador).first().id_firma
                id_firma_aprobador = Firma.objects.filter(id_documento=id_documento, id_liberador=aprobador).first().id_firma
                fecha_creacion = Documento.objects.get(id_documento=id_documento).fecha_inicio
                
                # Aquí puedes continuar con la lógica para firmar el documento usando la información obtenida
                # Recuerda manejar excepciones y errores según sea necesario
                
                return True
            else:
                return False
        except Exception as e:
            print(f"Error al firmar el documento: {str(e)}")
            return False    