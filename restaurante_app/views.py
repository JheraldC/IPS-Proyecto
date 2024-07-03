import json
from django.shortcuts import render, redirect, get_object_or_404
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
