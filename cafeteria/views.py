from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Q

from .models import Producto, Pedido, ItemPedido, Categoria, Pago
from .forms import RegistroForm, ProductoForm, AgregarItemForm, PagoForm, PedidoNotasForm, ActualizarEstadoForm


def es_admin(user):
    return user.is_staff


# ── Auth ──────────────────────────────────────────────────────────────────────

def registro(request):
    from django.contrib.auth.models import User

    hay_normales = User.objects.filter(is_staff=False, is_superuser=False).exists()
    hay_admins = User.objects.filter(is_staff=True).exists()
    registro_bloqueado = hay_normales and hay_admins

    if registro_bloqueado:
        messages.error(request, 'Ya existe al menos un usuario de cada tipo. No se pueden registrar más cuentas.')
        return redirect('login')

    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            tipo = form.cleaned_data.get('tipo')
            if tipo == 'normal' and hay_normales:
                messages.error(request, 'Ya existe un usuario normal.')
                return render(request, 'cafeteria/registro.html', {
                    'form': form, 'hay_normales': hay_normales, 'hay_admins': hay_admins
                })
            if tipo == 'admin' and hay_admins:
                messages.error(request, 'Ya existe un administrador.')
                return render(request, 'cafeteria/registro.html', {
                    'form': form, 'hay_normales': hay_normales, 'hay_admins': hay_admins
                })
            user = form.save(commit=False)
            if tipo == 'admin':
                user.is_staff = True
            user.save()
            login(request, user)
            messages.success(request, f'Bienvenido, {user.first_name}!')
            return redirect('menu')
    else:
        form = RegistroForm()

    return render(request, 'cafeteria/registro.html', {
        'form': form,
        'hay_normales': hay_normales,
        'hay_admins': hay_admins,
    })


# ── Menú (ListView genérica) ───────────────────────────────────────────────────

class MenuView(ListView):
    model = Producto
    template_name = 'cafeteria/menu.html'
    context_object_name = 'productos'

    def get_queryset(self):
        qs = Producto.objects.filter(disponible=True)
        q = self.request.GET.get('q')
        categoria = self.request.GET.get('categoria')
        if q:
            qs = qs.filter(Q(nombre__icontains=q) | Q(descripcion__icontains=q))
        if categoria:
            qs = qs.filter(categoria__id=categoria)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categorias'] = Categoria.objects.all()
        ctx['categoria_sel'] = self.request.GET.get('categoria', '')
        ctx['q'] = self.request.GET.get('q', '')
        return ctx


class ProductoDetailView(DetailView):
    model = Producto
    template_name = 'cafeteria/producto_detail.html'
    context_object_name = 'producto'


# ── Carrito / Pedido ──────────────────────────────────────────────────────────

def _get_or_create_carrito(user):
    pedido, _ = Pedido.objects.get_or_create(estudiante=user, estado='pendiente')
    return pedido


@login_required
def agregar_al_carrito(request, pk):
    producto = get_object_or_404(Producto, pk=pk, disponible=True)
    carrito = _get_or_create_carrito(request.user)
    item, created = ItemPedido.objects.get_or_create(pedido=carrito, producto=producto)
    if not created:
        item.cantidad += 1
        item.save()
    carrito.calcular_total()
    messages.success(request, f'{producto.nombre} agregado al carrito.')
    return redirect('carrito')


@login_required
def carrito(request):
    try:
        pedido = Pedido.objects.get(estudiante=request.user, estado='pendiente')
    except Pedido.DoesNotExist:
        pedido = None
    form = PedidoNotasForm(instance=pedido) if pedido else None
    return render(request, 'cafeteria/carrito.html', {'pedido': pedido, 'form': form})


@login_required
def eliminar_item(request, pk):
    item = get_object_or_404(ItemPedido, pk=pk, pedido__estudiante=request.user)
    pedido = item.pedido
    item.delete()
    pedido.calcular_total()
    messages.info(request, 'Producto eliminado del carrito.')
    return redirect('carrito')


@login_required
def actualizar_notas(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk, estudiante=request.user, estado='pendiente')
    if request.method == 'POST':
        form = PedidoNotasForm(request.POST, instance=pedido)
        if form.is_valid():
            form.save()
    return redirect('carrito')


# ── Pago ──────────────────────────────────────────────────────────────────────

@login_required
def pagar(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk, estudiante=request.user, estado='pendiente')
    if not pedido.items.exists():
        messages.error(request, 'El carrito está vacío.')
        return redirect('carrito')
    if request.method == 'POST':
        form = PagoForm(request.POST)
        if form.is_valid():
            pago = form.save(commit=False)
            pago.pedido = pedido
            pago.save()
            pedido.estado = 'en_preparacion'
            pedido.save()
            messages.success(request, f'Pago aprobado. Referencia: {pago.referencia}')
            return redirect('pedido_detalle', pk=pedido.pk)
    else:
        form = PagoForm()
    return render(request, 'cafeteria/pagar.html', {'pedido': pedido, 'form': form})


# ── Historial de pedidos ──────────────────────────────────────────────────────

class MisPedidosView(LoginRequiredMixin, ListView):
    model = Pedido
    template_name = 'cafeteria/mis_pedidos.html'
    context_object_name = 'pedidos'

    def get_queryset(self):
        return Pedido.objects.filter(
            estudiante=self.request.user
        ).exclude(estado='pendiente').order_by('-fecha_creacion')


class PedidoDetalleView(LoginRequiredMixin, DetailView):
    model = Pedido
    template_name = 'cafeteria/pedido_detalle.html'
    context_object_name = 'pedido'

    def get_queryset(self):
        if self.request.user.is_staff:
            return Pedido.objects.all()
        return Pedido.objects.filter(estudiante=self.request.user)


# ── Admin: CRUD Productos ─────────────────────────────────────────────────────

class ProductoListAdmin(LoginRequiredMixin, ListView):
    model = Producto
    template_name = 'cafeteria/admin_productos.html'
    context_object_name = 'productos'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('menu')
        return super().dispatch(request, *args, **kwargs)


class ProductoCreate(LoginRequiredMixin, CreateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'cafeteria/producto_form.html'
    success_url = reverse_lazy('admin_productos')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('menu')
        return super().dispatch(request, *args, **kwargs)


class ProductoUpdate(LoginRequiredMixin, UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'cafeteria/producto_form.html'
    success_url = reverse_lazy('admin_productos')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('menu')
        return super().dispatch(request, *args, **kwargs)


class ProductoDelete(LoginRequiredMixin, DeleteView):
    model = Producto
    template_name = 'cafeteria/producto_confirm_delete.html'
    success_url = reverse_lazy('admin_productos')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('menu')
        return super().dispatch(request, *args, **kwargs)


# ── Admin: gestión de pedidos ─────────────────────────────────────────────────

@user_passes_test(es_admin)
def admin_pedidos(request):
    estado = request.GET.get('estado', '')
    pedidos = Pedido.objects.exclude(estado='pendiente')
    if estado:
        pedidos = pedidos.filter(estado=estado)
    return render(request, 'cafeteria/admin_pedidos.html', {
        'pedidos': pedidos,
        'estado_sel': estado,
        'estados': Pedido.ESTADO_CHOICES,
    })


@user_passes_test(es_admin)
def actualizar_estado_pedido(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    if request.method == 'POST':
        form = ActualizarEstadoForm(request.POST, instance=pedido)
        if form.is_valid():
            form.save()
            messages.success(request, f'Pedido #{pk} actualizado a "{pedido.get_estado_display()}".')
    return redirect('admin_pedidos')
