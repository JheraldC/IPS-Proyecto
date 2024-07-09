from django.urls import path
from . import views
urlpatterns = [
    path("", views.index, name="index"),
    path('mesas/', views.mesas_view, name='mesas'),
    path('mesas/<int:mesa_numero>/detalle-pedido/', views.detalle_pedido, name='detalle_pedido'),
    path('pedidos/', views.pedidos, name='pedidos'),
    path('pedidos/<int:pedido_id>/descargar-ticket/', views.descargar_ticket, name='descargar_ticket'),
    path("login/", views.login_view, name="login"),
    path('logout/', views.logout_view, name='logout'),
]
