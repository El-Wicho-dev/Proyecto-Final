from django.shortcuts import render,redirect
from Usuarios.models import PerfilUsuario,Puesto,UsuarioPuesto
from Documentos.models import Plantilla
from Entrenamiento.models import EntrenamientoPuestoNomenclatura,Entrenamiento
from django.contrib.auth.models import User
from django.http import JsonResponse,HttpResponse
from django.db.models.functions import Cast,Concat
from django.db.models import CharField,Value
from django.contrib import messages
from django.utils import timezone
def actualizar_nomenclatura(request):
    template = 'Entrenamiento/actualizar_nomenclatura.html'
    
    usuarios_activos = PerfilUsuario.objects.filter(estado='ACTIVO')
    puestos = Puesto.objects.order_by('descripcion_general').values_list('descripcion_general', flat=True).distinct()
    nomenclaturas = EntrenamientoPuestoNomenclatura.objects.order_by('nomenclatura').values_list('nomenclatura', flat=True).distinct()

    if request.method == 'POST':
        print("POST data2:", request.POST)
        usuarios_nombres = request.POST.getlist('usuarios[]')
        usuariobool = request.POST.get('usuariobool', 'default_value')
        action = request.POST.get('action')

        print("POST data:", request.POST)
        print("Usuarios nombres:", usuarios_nombres)
        print("usuariobool:", usuariobool)
        
        nombres_puesto = []
        usuarios_ids = []
        descripciones_general = []
        lista_puestos_nomenclaturas = []

        if usuariobool == 'false':
            # Si la lista de nombres de usuarios está vacía, añade un mensaje de error
            messages.error(request, 'Por favor, seleccione al menos un usuario para el entrenamiento.')
            return redirect("update_nomenclature")
        else:
            for nombre_completo in usuarios_nombres:
                print("Procesando nombre:", nombre_completo)
                nomenclatura = request.POST.get("nomenclatura")  # Mover la asignación de nomenclatura aquí
                print("Nomenclatura recibida:", nomenclatura)

                usuarios_puestos = UsuarioPuesto.objects.annotate(
                    nombre_completo=Concat('usuario__first_name', Value(' '), 'usuario__last_name', output_field=CharField())
                ).filter(
                    nombre_completo=nombre_completo,
                    usuario__perfilusuario__estado='ACTIVO'
                )
                for up in usuarios_puestos:
                    print('Usuario activo encontrado:', up.nombre_completo)

                for usuario_puesto in usuarios_puestos:
                    if usuario_puesto.usuario.id not in usuarios_ids:
                        usuarios_ids.append(usuario_puesto.usuario.id)
                        nombre_completo = f"{usuario_puesto.usuario.first_name} {usuario_puesto.usuario.last_name}"
                        nombres_puesto.append(nombre_completo)
                        descripcion_general = usuario_puesto.puesto.descripcion_general
                        descripciones_general.append(descripcion_general)
                        lista_puestos_nomenclaturas.append(usuario_puesto.puesto.id)
                        print("Usuario activo agregado:", nombre_completo, "ID:", usuario_puesto.usuario.id, "Descripción:", usuario_puesto.puesto.descripcion_general, "ID Puesto:", usuario_puesto.puesto.id)
        
            print("Usuarios IDs:", usuarios_ids)
            print("Lista de puestos y nomenclaturas:", lista_puestos_nomenclaturas)

            print("Acción:", action)
            
            print("Ejecutando lógica de guardado")
            
            if action == 'sign':
                print("jeje")
                messages.success(request,"se actualizo el documento")
                # Descomentar y adaptar la lógica de guardado según tus necesidades
                """
                for puesto_id in lista_puestos_nomenclaturas:
                    puesto = Puesto.objects.get(id=puesto_id)
                    nuevo_entrenamiento = EntrenamientoPuestoNomenclatura(
                        id_puesto=puesto,
                        estado='ACTIVO',
                        fecha_registro=timezone.now(),
                        nomenclatura=nomenclatura,
                        id_unidad_negocio=None  # Siempre None como mencionaste
                    )
                    nuevo_entrenamiento.save()
                    print(f"Guardado: {nuevo_entrenamiento}")
                """
            return redirect('home')

            
    context = {
        'puestos': puestos,
        'usuarios_activos': usuarios_activos,
        'nomenclaturas': nomenclaturas
    }
    print(context)

    return render(request, template, context)





def puestoajax (request):
    if request.method == 'POST':
        #print(request.POST)
        descripcion_puesto = request.POST.get('puesto')
        
        #print(descripcion_puesto)
        
        nombres_puesto = []
        
        # Suponiendo que 'PerfilUsuario' tiene un campo 'estado' y está relacionado con 'User'
        usuarios_puestos = UsuarioPuesto.objects.filter(
            puesto__descripcion_general=descripcion_puesto,
            usuario__perfilusuario__estado='ACTIVO'
        )
        usuarios_distinct = usuarios_puestos.values('usuario__first_name', 'usuario__last_name').distinct()


        for usuario in usuarios_distinct:
            nombre_completo = f"{usuario['usuario__first_name']} {usuario['usuario__last_name']}"
            nombres_puesto.append(nombre_completo)

        #print(nombres_puesto)
        
        return JsonResponse({'nombres_puesto': nombres_puesto})


    
    return JsonResponse({'error': 'Método no permitido'})

def obtener_datos_usuarios(usuarios_nombres):
    nombres_puesto = []
    usuarios_ids = []
    descripciones_general = []

    for nombre_completo in usuarios_nombres:
        print("Procesando nombre:", nombre_completo)        
        
        usuarios_puestos = UsuarioPuesto.objects.annotate(
        nombre_completo=Concat('usuario__first_name', Value(' '), 'usuario__last_name', output_field=CharField())
        ).filter(
            nombre_completo=nombre_completo,
            usuario__perfilusuario__estado='ACTIVO'
        )
        print("Usuarios puestos activos encontrados:", usuarios_puestos)

        for usuario_puesto in usuarios_puestos:
            if usuario_puesto.usuario.id not in usuarios_ids:
                usuarios_ids.append(usuario_puesto.usuario.id)
                nombre_completo = f"{usuario_puesto.usuario.first_name} {usuario_puesto.usuario.last_name}"
                nombres_puesto.append(nombre_completo)
                descripcion_general = usuario_puesto.puesto.descripcion_general
                descripciones_general.append(descripcion_general)
                
                print("Usuario activo agregado:", nombre_completo, "ID:", usuario_puesto.usuario.id, "Descripcion: " , usuario_puesto.puesto.descripcion_general)
   

    return nombres_puesto, usuarios_ids, descripciones_general




def eliminar_nomenclatura(request):
    template = 'Entrenamiento/eliminar_nomenclatura.html'
    
    context = {
        
    }
    return render(request,template,context)
    
    
    
    
    
    
    
    