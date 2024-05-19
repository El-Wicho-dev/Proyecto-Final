from django.shortcuts import render, get_object_or_404, redirect
from Usuarios.models import Puesto
from Usuarios.forms import PuestoForm
# Create your views here.

def actualizar_puestos(request):
    if request.method == 'POST':
        form = PuestoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = PuestoForm()
    return render(request, 'Entrenamiento/actualizar_puesto.html', {'form': form})

    
    