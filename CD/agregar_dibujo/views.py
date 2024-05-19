from django.shortcuts import render

# Create your views here.


def adddrawing(request):
    template = 'documentos/agregar_dibujo.html'
    
    
    
    context = {
        
    }
    
    return render(request,template,context)