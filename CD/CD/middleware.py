from django.shortcuts import redirect
from django.conf import settings
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin


class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        login_url = reverse('login')  # Obtener la URL de inicio de sesión
        admin_url = reverse('admin:index')  # Obtener la URL de administración

        if not request.user.is_authenticated and request.path != login_url and not request.path.startswith(admin_url):
            return redirect('login')
        response = self.get_response(request)
        return response


class NoCacheMiddleware(MiddlewareMixin):
    
    def process_response(self, request, response):
        admin_url = reverse('admin:index')
        if request.path.startswith(admin_url):
            return response
    
    def process_response(self, request, response):
        if request.user.is_authenticated:
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        return response
