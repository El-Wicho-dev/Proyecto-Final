from django.db.models import F, Value, Case, When, CharField
from django.db.models.functions import Concat,Cast
from django.shortcuts import get_object_or_404
from Documentos.models  import Documento,Linea,Plantilla
from func.clases_de_documento import get_ruta_actual,nomenclatura
from django.conf import settings
from func.firmar_documento import  FirmarDocumentos 
import subprocess
import shutil
import os
from  func.clases_de_documento import get_ruta_obsoleta,get_ruta_actual
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

#Clase de guardar documento
class GuardarDocumento:
    def __init__(self, ruta_principal):
        self.ruta_principal = ruta_principal

    #Calcular la ruta del documento con respecto al di del documento
    def get_ruta(self,id_archivo):
        try:

            documentos = (Documento.objects
                .filter(id=id_archivo)
                .select_related('id_plantilla', 'id_linea', 'id_linea__area')  # Esto reemplaza los inner joins
                .annotate(
                    path=Case(
                        When(
                            id_linea__area__area='Departamento',
                            then=Concat(
                                F('id_plantilla__nombre'), Value('\\'),
                                F('id_linea__nombre_linea'), Value('\\')
                            ),
                        ),
                        default=Concat(F('id_plantilla__nombre'), Value('/')),
                        output_field=CharField(),
                    ),
                     nombre_plantilla=Case(
                        When(
                            id_plantilla__nombre__in=[
                                'Ayuda visual (Vertical)', 'Ayuda visual (Horizontal)'
                            ],
                            then=Value('Ayuda visual'),
                        ),
                        When(
                            id_plantilla__nombre__in=[
                                'Instrucciones de Operaciones (de proceso)', 'Instrucciones de Operaciones (de sistema)'
                            ],
                            then=Value('Instrucciones de Operaciones'),
                        ),
                        default=F('id_plantilla__nombre'),
                        output_field=CharField(),
                    ),
                    consecutivo_str=Case(
                        When(
                            consecutivo__lt=10,
                            then=Concat(Value('0'), Cast('consecutivo', output_field=CharField()))
                        ),
                        default=Cast('consecutivo', CharField()),
                        output_field=CharField()
                    ),
                    nombre_documento=Concat(
                        F('id_plantilla__codigo'), Value('-'),
                        F('id_linea__codigo_linea'), Value(' '),
                        F('consecutivo_str'), Value(' REV. '),
                        F('revision_documento'), Value(' '),
                        F('nombre'),
                        output_field=CharField(),
                    ),
                    full_path=Concat(
                        F('path'),
                        F('nombre_documento'),
                        output_field=CharField(),
                    )
                )
            )

            for doc in documentos:
                #print(doc.full_path)
                #print(doc.nombre_plantilla)
                #print(doc.id_linea.area.area)

                return doc.full_path
        except Documento.DoesNotExist:
            # Implementa tu lógica si el documento no se encuentra
            print("No se encontró el documento con ID: {}".format(id_archivo))

    #METODO PARA GUARDAR EL DOCUMENTO Y SI TIENE UNA REVISION ANTERIOR 
    #PONERLE MARCA DE AUGUA Y PONEERLO EN OBOSLETO 
    def guardar_documento(self,id_documento,nombre):
        print("si entre en guardar documento a obsoleto")
        
        ruta_original = GuardarDocumento.get_ruta(self,id_documento)
        # Si la ruta no termina en '.pdf', reemplazamos la extensión actual por '.pdf'
        if not ruta_original.endswith('.pdf'):
            ruta_base = ruta_original.rsplit('.', 1)[0]  # Remueve la extensión actual
            ruta_con_pdf = f'{ruta_base}.pdf'  # Añade la extensión '.pdf'
        else:
            ruta_con_pdf = ruta_original
                
        ruta_guardar_word = f'{settings.RUTA_EDITABLES_DOCUMENTOS} {ruta_original}'
        ruta_guardar_pdf =  f'{settings.RUTA_PDF_DOCUMENTOS} {ruta_con_pdf}'
        
        
        no_documento,no_linea,consecutivo,revision,nombre_del_documento = nomenclatura(nombre)
        print(nombre_del_documento)
    
        # Procesar versiones obsoletas si la revisión no es '00'
        if revision != "00":
            ruta_actual_obsoleta_word, ruta_guardar_obsoleta_word,base_path = get_ruta_obsoleta(id_documento)

            ruta_word_actual_obsoleta = settings.MEDIA_ROOT_EDITABLE + ruta_actual_obsoleta_word
            ruta_word_proximo_obsoleta = settings.MEDIA_ROOT_EDITABLE + ruta_guardar_obsoleta_word
            
            print(ruta_word_actual_obsoleta)
            print(ruta_word_proximo_obsoleta)
            
            ruta_actual_obsoleta_pdf = settings.MEDIA_ROOT_PDF + ruta_guardar_obsoleta_word.replace('.docx', '.pdf')
            ruta_guardar_obsoleta_pdf =  settings.MEDIA_ROOT_PDF + ruta_actual_obsoleta_word.replace('.docx', '.pdf')
            
            print("---------------------------")
            print('ruta a buscar ',ruta_guardar_obsoleta_pdf)
            print('ruta a pegar',ruta_actual_obsoleta_pdf)
            
            ruta_salida = os.path.join(settings.RUTA_PDF_DOCUMENTOS, base_path + '/OBSOLETO/')
            ruta_proecyecto = settings.MEDIA_ROOT

            
            print("Usuario actual:", os.getuid())
            print("Grupo actual:", os.getgid())
            print('la base path es: ' , base_path)
            print('la base path es ruta : ' , ruta_salida)

            print('la ruta BAE : ' , ruta_proecyecto)


            # Agregar marca de agua a la versión obsoleta del PDF
            self.add_watermark_to_pdf(ruta_guardar_obsoleta_pdf,ruta_actual_obsoleta_pdf, "OBSOLETO")
            
            self.process_word_document(ruta_word_actual_obsoleta,ruta_word_proximo_obsoleta)
            # Marcar documento anterior como obsoleto en la base de datos
            Documento.objects.filter(nombre=nombre_del_documento, estado='APROBADO').update(estado='OBSOLETO')


        
        
            
    #Metodo para agregar la marca de agua al documento OBSOLETO
    def add_watermark_to_pdf(self, pdf_path, output_path, watermark_text):
       
          # Extraer la ruta base y el nombre del archivo del output_path
        base_path, filename = os.path.split(output_path)

        # Verificar si 'OBSOLETO' está en la ruta base; si no, agregarlo
        if 'OBSOLETO' not in base_path:
            base_path = os.path.join(base_path, 'OBSOLETO')

        # Verificar si la carpeta existe, si no, crearla
        if not os.path.exists(base_path):
            os.makedirs(base_path)
            print(f"La carpeta {base_path} ha sido creada.")
        
        # Actualizar output_path para incluir la posible nueva carpeta 'OBSOLETO'
        output_path = os.path.join(base_path, filename)
            
        
        # Ruta del archivo de marca de agua temporal
        watermark_file = os.path.join(settings.TEMP_OUTPUT_DIR, "watermark.pdf")
        
        # Genera el PDF de la marca de agua con texto centrado en diagonal
        subprocess.run([
            'gs', '-o', watermark_file, '-sDEVICE=pdfwrite',
            '-c', "/Helvetica-Bold findfont 120 scalefont setfont",  # Incrementa el tamaño de la fuente
            '-c', "1 0.82 0.86 setrgbcolor",  # Establece el color del texto
            '-c', "297.5 421 translate",  # Centra el origen en la mitad de una página A4
            '-c', "45 rotate",  # Rota el texto 45 grados
            '-c', "-350 -50 moveto",  # Ajusta para centrar el texto rotado
            '-c', f"({watermark_text}) show"
        ], check=True)

        # Construye el archivo PDF final con la marca de agua
        try:
            subprocess.run([
                'pdftk', pdf_path, 'multistamp', watermark_file, 'output', output_path
            ], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error al aplicar la marca de agua: {e}")

        # Elimina el archivo de marca de agua temporal si se desea
        # os.remove(watermark_file)
        
        return output_path
    
    
            
        

    def process_word_document(self,input_path, new_path):
        
        os.makedirs(os.path.dirname(new_path), exist_ok=True)

        # Abrir el archivo original y copiarlo al nuevo destino
        with open(input_path, 'rb') as original_file:
            with open(new_path, 'wb') as new_file:
                new_file.write(original_file.read())
    



            

        
        
        
        
     


     
     
     
     
     
    