from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from .models import UsuarioPuesto

def descripcion_general_required(descripcion):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated:
                usuario_puesto = UsuarioPuesto.objects.filter(usuario=request.user).first()
                if usuario_puesto and usuario_puesto.puesto.descripcion_general == descripcion:
                    return view_func(request, *args, **kwargs)
            return HttpResponseForbidden("No tienes permiso para ver esta página.")
        return _wrapped_view
    return decorator

