from django.contrib import admin
from .models import CategoriaMenu, EstadoMenu, EstadoPedido, TipoUsuario, Usuario, Menu, Pedido, PedidoDetalle

# Register your models here.
admin.site.register(CategoriaMenu)
admin.site.register(EstadoMenu)
admin.site.register(EstadoPedido)
admin.site.register(TipoUsuario)
admin.site.register(Usuario)
admin.site.register(Menu)
admin.site.register(Pedido)
admin.site.register(PedidoDetalle)

