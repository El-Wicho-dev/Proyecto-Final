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


from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Value, CharField
from django.db.models.functions import Concat
from django.utils import timezone


#Actuliza la nomenclatura  y se le asginar a los usurios correspondientes
def actualizar_nomenclatura(request):
    template = 'Entrenamiento/actualizar_nomenclatura.html'
    
    usuarios_activos = PerfilUsuario.objects.filter(estado='ACTIVO')
    puestos = Puesto.objects.order_by('descripcion_general').values_list('descripcion_general', flat=True).distinct()
    nomenclaturas = EntrenamientoPuestoNomenclatura.objects.order_by('nomenclatura').values_list('nomenclatura', flat=True).distinct()

    if request.method == 'POST':
        try:
            action = request.POST.get('action')
            print("Acción recibida:", action)

            if action == 'sign':
                print("POST data2:", request.POST)
                usuarios_nombres = request.session.get('nombres_puesto', [])
                usuariobool = request.POST.get('usuariobool', 'default_value')
                nomenclatura = request.POST.get("nomenclatura")
                
                print("Usuarios nombres:", usuarios_nombres)
                print("usuariobool:", usuariobool)
                print("Nomenclatura recibida:", nomenclatura)

                nombres_puesto = []
                usuarios_ids = []
                descripciones_general = []
                lista_puestos_nomenclaturas = []

                if not usuarios_nombres or not nomenclatura:
                    print("yo entre al error")
                    messages.error(request, 'Por favor, agregue una nomenclatura y seleccione al menos un usuario para continuar.')
                     # Limpiar la sesión después de procesar los datos
                    request.session.pop('nombres_puesto', None)
                    return redirect('update_nomenclature')
                else:
                    for nombre_completo in usuarios_nombres:
                        print("Procesando nombre:", nombre_completo)
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
                    print("jeje")
                    
                    messages.success(request, "se actualizo el documento")
                    # Descomentar y adaptar la lógica de guardado según tus necesidades
                    #Aqui se inserta la nomenclantura con losp ues correspondientes
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
                    
                     # Limpiar la sesión después de procesar los datos
                    request.session.pop('nombres_puesto', None)
                    return redirect('home')

        except Exception as e:
            print("Se produjo un error:", str(e))
            messages.error(request, f'Se produjo un error al procesar la solicitud: {str(e)}')
            return redirect('update_nomenclature')
            
    context = {
        'puestos': puestos,
        'usuarios_activos': usuarios_activos,
        'nomenclaturas': nomenclaturas
    }
    #print(context)

    return render(request, template, context)



#Este es uajax de javascript para mandar lso puestos correspondinetes
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


        request.session['nombres_puesto'] = nombres_puesto

        #print(nombres_puesto)
        
        return JsonResponse({'nombres_puesto': nombres_puesto})

    return JsonResponse({'error': 'Método no permitido'})



def obtener_usuarios_por_puesto(request):
    if request.method == 'POST':
        puesto = request.POST.get('puesto')
        # Aquí iría la lógica para obtener los usuarios basados en el puesto
        # Supongamos que tienes una lista de usuarios para cada puesto
        usuarios = {
            'Puesto1': ['Usuario1', 'Usuario2'],
            'Puesto2': ['Usuario3', 'Usuario4'],
            # Añade más puestos y usuarios según sea necesario
        }
        nombres_puesto = usuarios.get(puesto, [])
        return JsonResponse({'nombres_puesto': nombres_puesto})
    return JsonResponse({'error': 'Método no permitido'}, status=405)





def obtener_datos_usuarios(usuarios_nombres):
    nombres_puesto = []
    usuarios_ids = []
    descripciones_general = []

    for nombre_completo in usuarios_nombres:
        #print("Procesando nombre:", nombre_completo)        
        
        usuarios_puestos = UsuarioPuesto.objects.annotate(
        nombre_completo=Concat('usuario__first_name', Value(' '), 'usuario__last_name', output_field=CharField())
        ).filter(
            nombre_completo=nombre_completo,
            usuario__perfilusuario__estado='ACTIVO'
        )
        #print("Usuarios puestos activos encontrados:", usuarios_puestos)

        for usuario_puesto in usuarios_puestos:
            if usuario_puesto.usuario.id not in usuarios_ids:
                usuarios_ids.append(usuario_puesto.usuario.id)
                nombre_completo = f"{usuario_puesto.usuario.first_name} {usuario_puesto.usuario.last_name}"
                nombres_puesto.append(nombre_completo)
                descripcion_general = usuario_puesto.puesto.descripcion_general
                descripciones_general.append(descripcion_general)
                
                #print("Usuario activo agregado:", nombre_completo, "ID:", usuario_puesto.usuario.id, "Descripcion: " , usuario_puesto.puesto.descripcion_general)
   

    return nombres_puesto, usuarios_ids, descripciones_general




def eliminar_nomenclatura(request):
    template = 'Entrenamiento/eliminar_nomenclatura.html'
    
    context = {
        
    }
    return render(request,template,context)
    
    
    
    
    
    
    
    