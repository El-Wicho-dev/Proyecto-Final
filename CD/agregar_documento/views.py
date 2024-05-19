from django.shortcuts import render

# Create your views here.

def agregar(request):
    #pdf_url = '/media/Calidad/calidad.pdf'  # Asegúrate de usar el nombre correcto del archivo
    return render(request,'documentos/agregar_documento.html',{})
