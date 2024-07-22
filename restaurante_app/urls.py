from django.urls import path
from . import views
urlpatterns = [
    path("", views.index, name="index"),

    #gestion
    path('mesas/', views.mesas_view, name='mesas'),
    path('mesas/<int:mesa_numero>/detalle-pedido/', views.detalle_pedido, name='detalle_pedido'),
    path('pedidos/', views.pedidos_view, name='pedidos'),
    path('pedidos/<int:pedido_id>/descargar-ticket/', views.descargar_ticket, name='descargar_ticket'),
    path('actualizar_estado_pedido/<int:pedido_id>/', views.actualizar_estado_pedido, name='actualizar_estado_pedido'),
    path('obtener_pedidos_json/', views.obtener_pedidos_json, name='obtener_pedidos_json'),
    path('limpiar_mesa/<int:mesa_id>/', views.limpiar_mesa, name='limpiar_mesa'),
    path('pedido-creado/<int:pedido_id>/', views.pedido_creado, name='pedido_creado'),

    #Admin
    #Platos
    path('platos/', views.platos_admin, name='platos_admin'),
    path('platos/crear/', views.crear_plato, name='crear_plato'),
    path('platos/<int:plato_id>/editar/', views.editar_plato, name='editar_plato'),
    path('platos/<int:plato_id>/eliminar/', views.eliminar_plato, name='eliminar_plato'),

    #Categorias
    path('categorias/', views.categorias_admin, name='categorias_admin'),
    path('categorias/crear/', views.crear_categoria, name='crear_categoria'),
    path('categorias/<int:categoria_id>/editar/', views.editar_categoria, name='editar_categoria'),
    path('categorias/<int:categoria_id>/eliminar/', views.eliminar_categoria, name='eliminar_categoria'),
    
    #Mesas
    path('mesas-admin/', views.mesas_admin, name='mesas_admin'),
    path('mesas-admin/crear/', views.crear_mesa, name='crear_mesa'),
    path('mesas-admin/<int:mesa_numero>/eliminar/', views.eliminar_mesa, name='eliminar_mesa'),

    #Usuarios
    path('usuarios/', views.usuarios_admin, name='usuarios_admin'),

    #inicio y cerrar
    path("login/", views.login_view, name="login"),
    path('logout/', views.logout_view, name='logout'),
]
