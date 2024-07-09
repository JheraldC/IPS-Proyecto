import json
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from datetime import date
from django.http import JsonResponse
from .models import Mesa, Pedido, PedidoDetalle, Usuario, EstadoMesa, EstadoPedido, CategoriaMenu, Menu
from django.db.models import Sum
from .forms import AbrirMesaForm 
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
def mesas_view(request):
    mesas = Mesa.objects.all()
    mozos = Usuario.objects.filter(TipUsuCod__TipUsuDes="Mozo")
    mesa_seleccionada = None
    form = AbrirMesaForm()  # Crea una instancia del formulario siempre

    if request.method == 'POST':
        mesa_numero = request.POST.get('numero')  # Obtén el número de mesa del formulario
        if mesa_numero:
            mesa_seleccionada = get_object_or_404(Mesa, numero=mesa_numero)

            if mesa_seleccionada.EstMesCod.EstMesDes == 'libre':
                form = AbrirMesaForm(request.POST, instance=mesa_seleccionada)  # Pasa la instancia de mesa al formulario
                if form.is_valid():
                    mesa = form.save(commit=False)
                    mesa.EstMesCod = EstadoMesa.objects.get(EstMesDes='ocupado')
                    mesa.save()

                    return redirect('detalle_pedido', mesa_numero=mesa.numero)
            else:  # Si la mesa ya está ocupada, redirige directamente a detalle_pedido
                return redirect('detalle_pedido', mesa_numero=mesa_numero)

    else:  # Si es GET, verifica si se pasó un número de mesa en la URL
        mesa_numero = request.GET.get('mesa_numero')
        if mesa_numero:
            mesa_seleccionada = get_object_or_404(Mesa, numero=mesa_numero)
            form = AbrirMesaForm(initial={'numero': mesa_numero, 'mozo': request.user})  # Preselecciona el mozo actual

    return render(request, 'mesas.html', {
        'mesas': mesas,
        'mesa_seleccionada': mesa_seleccionada,
        'mozos': mozos,
        'form': form,
    })

@login_required
def detalle_pedido(request, mesa_numero):
    mesa = get_object_or_404(Mesa, numero=mesa_numero)

    # Obtener o crear el estado "En proceso"
    estado_en_proceso, _ = EstadoPedido.objects.get_or_create(EstPedDes='enproceso')

    # Obtener o crear el pedido, proporcionando el ID del estado directamente
    pedido, created = Pedido.objects.get_or_create(
        MesCod=mesa,
        defaults={
            'MozCod': request.user,
            'PedFec': date.today(),
            'PedHor': timezone.now(),
            'PedCli': request.POST.get('cliente'), #guardamos el pedido
            'PedTot': 0,
            'PedObs': request.POST.get('comentarios'),
            'EstPedCod': estado_en_proceso,  # Asignar el estado obtenido
        }
    )

    categorias = CategoriaMenu.objects.all()
    platos = Menu.objects.filter(EstMenCod__EstMenDes='disponible') # Filtramos los platos disponibles
    platos_json = serializers.serialize('json', platos)  # Serializa los platos a JSON
    detalles_pedido = pedido.detalles.all()
    detalles_pedido_json = serializers.serialize("json", detalles_pedido)

    if request.method == 'POST':
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                data = json.loads(request.body)
                plato_id = data.get('plato_id')
                comentarios_mesa = data.get('comentarios', '')  # Obtener los comentarios como una cadena de texto
                cantidad = data.get('cantidad')
                finalizar_venta = data.get('finalizar_venta')

                if finalizar_venta:
                    # 1. Actualizamos el pedido con comentarios (si los hay)
                    pedido.PedObs = data.get('comentarios', '')
                    pedido.save()
                
                    # 2. Creamos los PedidoDetalle
                    for plato_id, cantidad in data.get('platos', {}).items():
                        if cantidad > 0:
                            plato = Menu.objects.get(MenCod=plato_id)
                            PedidoDetalle.objects.create(
                                PedCod=pedido,
                                MenCod=plato,
                                PedCan=cantidad,
                                PedSub=plato.precio * cantidad
                            )
                
                    # 3. Redirigimos a la vista de generar_ticket
                    return JsonResponse({
                        'success': True,
                        'pedido_id': pedido.PedCod,  # Incluimos el ID del pedido
                        'redirect_url': reverse('descargar_ticket', args=[pedido.PedCod])
                    })
                else:
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
                    pedido.PedTot = pedido.detalles.aggregate(Sum('PedSub'))['PedSub__sum'] or 0
                    pedido.PedObs = comentarios_mesa
                    pedido.save()

                    return JsonResponse({
                        'success': True, 
                        'total': pedido.PedTot, 
                        'detalles_pedido': list(detalles_pedido.values('MenCod__MenDes', 'PedCan', 'PedSub'))
                    })

            except (json.JSONDecodeError, Menu.DoesNotExist) as e:
                return JsonResponse({'success': False, 'error': str(e)})

    return render(request, 'detalle_pedido.html', {
        'mesa': mesa,
        'pedido': pedido,
        'categorias': categorias,
        'platos': platos,
        'platos_json': platos_json,  # Pasar los platos serializados en JSON
        'detalles_pedido': detalles_pedido,
        'detalles_pedido_json': detalles_pedido_json,
    })

@login_required
def descargar_ticket(request, pedido_id):
    pedido = get_object_or_404(Pedido, PedCod=pedido_id)

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
