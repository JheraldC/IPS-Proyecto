import json
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.serializers.json import DjangoJSONEncoder
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.utils import timezone
from datetime import date
from django.http import JsonResponse
from .models import Mesa, Pedido, PedidoDetalle, Usuario, EstadoMesa, EstadoPedido, CategoriaMenu, Menu
from django.db.models import Sum
from .forms import AbrirMesaForm, MenuForm
from django.core import serializers

def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/') 
        else:
            return render(request, 'login.html', {'error': 'Credenciales no válidas'})
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('index')

@login_required
def index(request):
    return render(request, 'index.html')

@login_required
def pedidos_view(request):
    pedidos_en_proceso = Pedido.objects.filter(EstPedCod_id=1).prefetch_related('detalles').values()
    pedidos_cancelados = Pedido.objects.filter(EstPedCod_id=2).prefetch_related('detalles').values()
    pedidos_finalizados = Pedido.objects.filter(EstPedCod_id=3).prefetch_related('detalles').values()

    pedidos_con_detalles = []
    for queryset in [pedidos_cancelados, pedidos_en_proceso, pedidos_finalizados]:
        for pedido in queryset:
            detalles = list(PedidoDetalle.objects.filter(PedCod_id=pedido['PedCod']).values(
                'PedCan', 'MenCod__MenDes'  # Incluye el nombre del plato en la consulta
            ))
            pedido['DetPed'] = detalles
            pedidos_con_detalles.append(pedido)

    # Serializar los datos a JSON usando DjangoJSONEncoder
    pedidos_en_proceso_json = json.dumps([p for p in pedidos_con_detalles if p['EstPedCod_id'] == 1], cls=DjangoJSONEncoder)
    pedidos_cancelados_json = json.dumps([p for p in pedidos_con_detalles if p['EstPedCod_id'] == 2], cls=DjangoJSONEncoder)
    pedidos_finalizados_json = json.dumps([p for p in pedidos_con_detalles if p['EstPedCod_id'] == 3], cls=DjangoJSONEncoder)

    return render(request, 'pedidos.html', {
        'pedidos_cancelados': pedidos_cancelados_json,
        'pedidos_en_proceso': pedidos_en_proceso_json,
        'pedidos_finalizados': pedidos_finalizados_json,
    })

def actualizar_estado_pedido(request, pedido_id):
    if request.method == 'POST':
        try:
            pedido = Pedido.objects.get(pk=pedido_id)
            pedido.EstPedCod_id = 3  # Cambiar el estado a "Finalizado"
            mesa = pedido.MesCod
            mesa.EstMesCod = EstadoMesa.objects.get(EstMesDes='sucio')
            pedido.save()
            mesa.save()
            return JsonResponse({'success': True, 'pedido_id': pedido_id})
        except Pedido.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Pedido no encontrado'})
    else:
        return JsonResponse({'success': False, 'error': 'Método no permitido'})

def limpiar_mesa(request, mesa_id):
    if request.method == 'POST':
        try:
            mesa = Mesa.objects.get(pk=mesa_id)
            mesa.EstMesCod = EstadoMesa.objects.get(EstMesDes='disponible')
            mesa.save()
            return JsonResponse({'success': True})
        except Mesa.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Mesa no encontrada'})
    else:
        return JsonResponse({'success': False, 'error': 'Método no permitido'})

def obtener_pedidos_json(request):
    pedidos_cancelados = list(Pedido.objects.filter(EstPedCod_id=1).prefetch_related('detalles').values())
    pedidos_en_proceso = list(Pedido.objects.filter(EstPedCod_id=2).prefetch_related('detalles').values())
    pedidos_finalizados = list(Pedido.objects.filter(EstPedCod_id=3).prefetch_related('detalles').values())

    # Asegurar que 'DetPed' sea una lista, incluso si está vacía
    for pedidos in [pedidos_cancelados, pedidos_en_proceso, pedidos_finalizados]:
        for pedido in pedidos:
            pedido['DetPed'] = list(pedido.get('detalles', []))

    return JsonResponse({
        'pedidos_cancelados': pedidos_cancelados,
        'pedidos_en_proceso': pedidos_en_proceso,
        'pedidos_finalizados': pedidos_finalizados
    }, encoder=DjangoJSONEncoder, safe=False)

@login_required
def mesas_view(request):
    mesas = Mesa.objects.all()
    mozos = Usuario.objects.filter(TipUsuCod__TipUsuDes="Mozo")
    mesa_seleccionada = None
    form = AbrirMesaForm()  # Crea una instancia del formulario siempre

    if request.method == 'POST':
        mesa_numero = request.POST.get('numero')  # Obtén el número de mesa del formulario
        print(mesa_numero)
        if mesa_numero:
            mesa_seleccionada = get_object_or_404(Mesa, numero=mesa_numero)
            if mesa_seleccionada.EstMesCod.EstMesDes == 'disponible':
                form = AbrirMesaForm(request.POST, instance=mesa_seleccionada)  # Pasa la instancia de mesa al formulario
                if form.is_valid():
                    # Almacenar el ID del mozo en la sesión
                    request.session['abrir_mesa_form_data'] = {
                        'num_personas': form.cleaned_data['num_personas'],
                        'cliente': form.cleaned_data['cliente'],
                        'mozo_id': form.cleaned_data['mozo'].id,  # Almacenar el ID del mozo
                        'comentarios': form.cleaned_data['comentarios'],
                    }
                    print(form.cleaned_data)

                    mesa = form.save(commit=False)
                    return redirect('detalle_pedido', mesa_numero=mesa.numero)
                else:
                    print("Errores de validación del formulario:", form.errors)  # Imprimir errores de validación

    else:  # Si es GET, verifica si se pasó un número de mesa en la URL
        mesa_numero = request.GET.get('mesa_numero')
        if mesa_numero:
            mesa_seleccionada = get_object_or_404(Mesa, numero=mesa_numero)
            form = AbrirMesaForm(initial={'numero': mesa_numero, 'mozo': request.user})  # Preselecciona el mozo actual
            if mesa_seleccionada.EstMesCod.EstMesDes == 'ocupado':
                # Si la mesa está ocupada, muestra un mensaje
                mensaje_ocupada = "La mesa ya está ocupada."
                return render(request, 'mesas.html', {
                    'mesas': mesas,
                    'mesa_seleccionada': mesa_seleccionada,
                    'mozos': mozos,
                    'form': form,
                    'mensaje': mensaje_ocupada,
                })
            elif mesa_seleccionada.EstMesCod.EstMesDes == 'sucio':
                mensaje_sucia = "La mesa está sucia."
                return render(request, 'mesas.html', {
                    'mesas': mesas,
                    'mesa_seleccionada': mesa_seleccionada,
                    'mozos': mozos,
                    'form': form,
                    'mensaje_sucio': mensaje_sucia,
                })

    return render(request, 'mesas.html', {
        'mesas': mesas,
        'mesa_seleccionada': mesa_seleccionada,
        'mozos': mozos,
        'form': form,
    })

@login_required
def detalle_pedido(request, mesa_numero):
    mesa = get_object_or_404(Mesa, numero=mesa_numero)
    if mesa.EstMesCod.EstMesDes == 'ocupado':
        # Si está ocupada, redirige a la vista de mesas
        return redirect('mesas')

    # Obtener o crear el estado "En proceso"
    estado_en_proceso, _ = EstadoPedido.objects.get_or_create(EstPedDes='enproceso')
    pedido = None  # Inicializar pedido como None

    categorias = CategoriaMenu.objects.all()
    platos = Menu.objects.filter(EstMenCod__EstMenDes='disponible') # Filtramos los platos disponibles
    platos_json = serializers.serialize('json', platos)  # Serializa los platos a JSON

    form_data = request.session.get('abrir_mesa_form_data', None)

    if form_data:
        num_personas = form_data['num_personas']
        cliente = form_data['cliente']
        comentarios = form_data['comentarios']

        # Obtener el objeto Usuario del mozo a partir del ID almacenado en la sesión
        mozo_id = form_data['mozo_id']
        mozo = Usuario.objects.get(id=mozo_id)
    else:
        return redirect('mesas')

    if request.method == "POST":
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                data = json.loads(request.body)
                plato_id = data.get('plato_id')
                cantidad = data.get('cantidad')
                finalizar_venta = data.get('finalizar_venta')

                if finalizar_venta and not pedido and data.get('platos'):
                    pedido = Pedido.objects.create(
                        MesCod=mesa,
                        MozCod=mozo,
                        PedFec=date.today(),
                        PedHor=timezone.now(),
                        PedCli=cliente,
                        PedTot=0,
                        PedObs=comentarios,
                        EstPedCod=estado_en_proceso,
                        PedNumPer=num_personas,  # Añadir número de personas
                    )
                    # 1. Creamos los PedidoDetalle
                    for plato_id, cantidad in data.get('platos', {}).items():
                        if cantidad > 0:
                            plato = Menu.objects.get(MenCod=plato_id)
                            detalle, created = PedidoDetalle.objects.update_or_create(
                                PedCod=pedido,
                                MenCod=plato,
                                PedCan=cantidad,
                                PedSub=plato.precio * cantidad,
                            )
                            if created:
                                # Cambiar el estado de la mesa a "ocupada"
                                mesa.EstMesCod = EstadoMesa.objects.get(EstMesDes='ocupado')
                                mesa.save()
                    # 2. Redirigimos a la vista de generar_ticket
                    pedido.PedTot = pedido.detalles.aggregate(Sum('PedSub'))['PedSub__sum'] or 0
                    pedido.save()
                    # Respuesta exitosa (JSON)
                    return JsonResponse({
                        'success': True,
                        'pedido_id': pedido.PedCod,
                        'redirect_url': reverse('descargar_ticket', args=[pedido.PedCod])
                    })
                elif not finalizar_venta and plato_id and cantidad:
                    # Si no se está finalizando, verificar si el pedido ya existe
                    if not pedido:
                        return JsonResponse({'success': False, 'error': 'El pedido no ha sido creado aún.'})

                    plato = Menu.objects.get(MenCod=plato_id)
                    subtotal = plato.precio * cantidad

                    # Actualizar o crear el detalle del pedido
                    detalle, created = PedidoDetalle.objects.get_or_create(
                        PedCod=pedido,
                        MenCod=plato,
                        defaults={'PedCan': 0}  # Valor inicial para PedCan si no existe
                    )
                    detalle.PedCan += cantidad
                    detalle.PedSub = subtotal
                    detalle.save()

                    # Actualizar el total del pedido
                    detalles_pedido = pedido.detalles.all()
                    # Respuesta exitosa (JSON) al agregar platos
                    return JsonResponse({
                        'success': True,
                        'total': pedido.PedTot,
                        'detalles_pedido': list(detalles_pedido.values('MenCod__MenDes', 'PedCan', 'PedSub'))
                    })

                else:
                    return JsonResponse({'success': False, 'error': 'Datos incompletos para crear el pedido.'})

            except (json.JSONDecodeError, Menu.DoesNotExist, Exception) as e:
                # Respuesta de error (JSON) en caso de excepción
                return JsonResponse({'success': False, 'error': str(e)})

    # Mover la consulta de detalles_pedido fuera del bloque if
    if pedido:  # Verificar si pedido existe antes de acceder a detalles
        detalles_pedido = pedido.detalles.all()
    else:
        detalles_pedido = []  # Si pedido es None, inicializar con una lista vacía

    detalles_pedido_json = serializers.serialize("json", detalles_pedido)

    return render(request, 'detalle_pedido.html', {
        'mesa': mesa,
        'pedido': pedido,
        'categorias': categorias,
        'platos': platos,
        'platos_json': platos_json,  # Pasar los platos serializados en JSON
        'detalles_pedido': detalles_pedido,
        'detalles_pedido_json': detalles_pedido_json,
        'form_data': form_data,  # Pasar los datos del formulario al contexto
    })

@login_required
def descargar_ticket(request, pedido_id):
    pedido = get_object_or_404(Pedido, PedCod=pedido_id)

    # Configuración de la respuesta HTTP (colocar aquí)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ticket_pedido_{pedido_id}.pdf"'

    # Configuración de la respuesta HTTP
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ticket_pedido_{pedido_id}.pdf"'

    # Crear el documento PDF
    doc = SimpleDocTemplate(response, pagesize=letter)

    # Estilos
    styles = getSampleStyleSheet()
    styleN = styles['Normal']
    styleH = styles['Heading1']

    # Contenido del ticket
    story = []

    story.append(Paragraph("Restaurante XYZ", styleH))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(f"Mesa: {pedido.MesCod.numero}", styleN))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(f"Comanda #{pedido_id:06d}", styleN))  # Formato de 6 dígitos con ceros a la izquierda
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(f"{pedido.PedFec.strftime('%d/%m/%y')} - {pedido.PedHor.strftime('%I:%M:%S %p')}", styleN))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(f"MOZO: {pedido.MozCod.username}", styleN))
    story.append(Spacer(1, 0.2*inch))

    # Tabla de detalles del pedido
    data = [["Cantidad", "Plato", "Subtotal"]]
    for detalle in pedido.detalles.all():
        data.append([detalle.PedCan, detalle.MenCod.MenDes, f"S/. {detalle.PedSub:.2f}"])

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), '#EEEEEE'),
        ('TEXTCOLOR', (0,0), (-1,0), '#000000'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 12),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,1), (-1,-1), '#FFFFFF'),
        ('GRID', (0,0), (-1,-1), 1, '#DDDDDD')
    ]))
    story.append(table)
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("********************************************************************", styleN))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(f"TOTAL: S/. {pedido.PedTot:.2f}", styleN))

    # Construir el documento PDF
    doc.build(story)

    return response 

@login_required
def pedido_creado(request, pedido_id):
    pedido = get_object_or_404(Pedido, PedCod=pedido_id)
    return render(request, 'pedido_creado.html', {'pedido': pedido})

# ADMIN

# Vistas CRUD para Platos (Menu)
@login_required
def platos_admin(request):
    if request.user.TipUsuCod.TipUsuDes != "Administrador":
        return redirect('index')

    platos = Menu.objects.all()
    return render(request, 'platos_admin.html', {'platos': platos})

@login_required
def crear_plato(request):
    if request.user.TipUsuCod.TipUsuDes != "Administrador":
        return redirect('index')

    if request.method == 'POST':
        form = MenuForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('platos_admin')
    else:
        form = MenuForm()
    return render(request, 'crear_plato.html', {'form': form})

@login_required
def editar_plato(request, plato_id):
    if request.user.TipUsuCod.TipUsuDes != "Administrador":
        return redirect('index')

    plato = get_object_or_404(Menu, MenCod=plato_id)
    if request.method == 'POST':
        form = MenuForm(request.POST, instance=plato)
        if form.is_valid():
            form.save()
            return redirect('platos_admin')
    else:
        form = MenuForm(instance=plato)
    return render(request, 'editar_plato.html', {'form': form, 'plato': plato})

@login_required
def eliminar_plato(request, plato_id):
    if request.user.TipUsuCod.TipUsuDes != "Administrador":
        return redirect('index')

    plato = get_object_or_404(Menu, MenCod=plato_id)
    if request.method == 'POST':
        plato.delete()
        return redirect('platos_admin')
    return render(request, 'eliminar_plato.html', {'plato': plato})

# Vistas CRUD para Categorías (CategoriaMenu)
@login_required
def categorias_admin(request):
    # ... (lógica para listar, crear, actualizar y eliminar categorías) ...
    return 0

# Vistas CRUD para Mesas (Mesa)
@login_required
def mesas_admin(request):
    # ... (lógica para listar, crear, actualizar y eliminar mesas) ...
    return 0

# Vistas CRUD para Usuarios (Usuario)
@login_required
def usuarios_admin(request):
    # ... (lógica para listar, crear, actualizar y eliminar usuarios) ...
    return 0
