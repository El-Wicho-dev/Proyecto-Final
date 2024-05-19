from django.shortcuts import render

# Create your views here.

def solicitar(request):
    template_name = 'documentos/solicitar_liberacion.html'
    
    return render  (request,template_name,{})