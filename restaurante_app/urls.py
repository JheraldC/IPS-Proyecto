from django.urls import path
from . import views
urlpatterns = [
    path("", views.index, name="index"),
    path('mesas/', views.mesas_view, name='mesas'),
    path('mesas/<int:mesa_numero>/detalle-pedido/', views.detalle_pedido, name='detalle_pedido'),
    path('pedidos/', views.pedidos_view, name='pedidos'),
    path('pedidos/<int:pedido_id>/descargar-ticket/', views.descargar_ticket, name='descargar_ticket'),
    path('actualizar_estado_pedido/<int:pedido_id>/', views.actualizar_estado_pedido, name='actualizar_estado_pedido'),
    path('obtener_pedidos_json/', views.obtener_pedidos_json, name='obtener_pedidos_json'),
    path('limpiar_mesa/<int:mesa_id>/', views.limpiar_mesa, name='limpiar_mesa'),
    path('pedido-creado/<int:pedido_id>/', views.pedido_creado, name='pedido_creado'),
    path("login/", views.login_view, name="login"),
    path('logout/', views.logout_view, name='logout'),
]
