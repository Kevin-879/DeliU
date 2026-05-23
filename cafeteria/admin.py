from django.contrib import admin
from .models import Categoria, Producto, Pedido, ItemPedido, Pago


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'descripcion']
    search_fields = ['nombre']


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'categoria', 'precio', 'disponible', 'tiempo_preparacion']
    list_filter = ['disponible', 'categoria']
    list_editable = ['disponible', 'precio']
    search_fields = ['nombre']


class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0
    readonly_fields = ['subtotal']

    def subtotal(self, obj):
        return obj.subtotal()


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ['id', 'estudiante', 'estado', 'total', 'fecha_creacion']
    list_filter = ['estado']
    list_editable = ['estado']
    search_fields = ['estudiante__username']
    inlines = [ItemPedidoInline]
    readonly_fields = ['total', 'fecha_creacion', 'fecha_actualizacion']


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ['referencia', 'pedido', 'metodo', 'estado', 'fecha']
    list_filter = ['estado', 'metodo']
    readonly_fields = ['referencia', 'fecha']
