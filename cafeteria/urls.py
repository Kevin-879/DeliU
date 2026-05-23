from django.urls import path
from . import views

urlpatterns = [
    path('', views.MenuView.as_view(), name='menu'),
    path('registro/', views.registro, name='registro'),
    path('producto/<int:pk>/', views.ProductoDetailView.as_view(), name='producto_detalle'),

    # Carrito
    path('carrito/', views.carrito, name='carrito'),
    path('carrito/agregar/<int:pk>/', views.agregar_al_carrito, name='agregar_carrito'),
    path('carrito/eliminar/<int:pk>/', views.eliminar_item, name='eliminar_item'),
    path('carrito/notas/<int:pk>/', views.actualizar_notas, name='actualizar_notas'),

    # Pago
    path('pagar/<int:pk>/', views.pagar, name='pagar'),

    # Pedidos
    path('mis-pedidos/', views.MisPedidosView.as_view(), name='mis_pedidos'),
    path('pedido/<int:pk>/', views.PedidoDetalleView.as_view(), name='pedido_detalle'),

    # Admin productos CRUD
    path('admin-panel/productos/', views.ProductoListAdmin.as_view(), name='admin_productos'),
    path('admin-panel/productos/nuevo/', views.ProductoCreate.as_view(), name='producto_crear'),
    path('admin-panel/productos/<int:pk>/editar/', views.ProductoUpdate.as_view(), name='producto_editar'),
    path('admin-panel/productos/<int:pk>/eliminar/', views.ProductoDelete.as_view(), name='producto_eliminar'),

    # Admin pedidos
    path('admin-panel/pedidos/', views.admin_pedidos, name='admin_pedidos'),
    path('admin-panel/pedidos/<int:pk>/estado/', views.actualizar_estado_pedido, name='actualizar_estado'),
]
