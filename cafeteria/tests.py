from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal

from .models import Categoria, Producto, Pedido, ItemPedido, Pago


class ModelosTest(TestCase):
    def setUp(self):
        self.categoria = Categoria.objects.create(nombre='Bebidas')
        self.producto = Producto.objects.create(
            nombre='Café', precio=Decimal('3500'), categoria=self.categoria
        )
        self.user = User.objects.create_user('estudiante1', password='pass1234')

    def test_producto_str(self):
        self.assertIn('Café', str(self.producto))

    def test_pedido_calcular_total(self):
        pedido = Pedido.objects.create(estudiante=self.user)
        ItemPedido.objects.create(pedido=pedido, producto=self.producto, cantidad=2)
        pedido.calcular_total()
        self.assertEqual(pedido.total, Decimal('7000'))

    def test_item_subtotal(self):
        pedido = Pedido.objects.create(estudiante=self.user)
        item = ItemPedido.objects.create(pedido=pedido, producto=self.producto, cantidad=3)
        self.assertEqual(item.subtotal(), Decimal('10500'))


class VistasTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('test_user', password='pass1234')
        self.admin = User.objects.create_superuser('admin_user', password='admin1234')
        self.cat = Categoria.objects.create(nombre='Comida')
        self.producto = Producto.objects.create(
            nombre='Arepa', precio=Decimal('2000'), categoria=self.cat
        )

    def test_menu_accesible_sin_login(self):
        r = self.client.get(reverse('menu'))
        self.assertEqual(r.status_code, 200)

    def test_menu_muestra_productos(self):
        r = self.client.get(reverse('menu'))
        self.assertContains(r, 'Arepa')

    def test_carrito_requiere_login(self):
        r = self.client.get(reverse('carrito'))
        self.assertRedirects(r, '/login/?next=/carrito/')

    def test_agregar_al_carrito(self):
        self.client.login(username='test_user', password='pass1234')
        r = self.client.get(reverse('agregar_carrito', args=[self.producto.pk]))
        self.assertEqual(r.status_code, 302)
        self.assertTrue(Pedido.objects.filter(estudiante=self.user, estado='pendiente').exists())

    def test_registro_usuario(self):
        r = self.client.post(reverse('registro'), {
            'username': 'nuevo', 'first_name': 'Ana', 'last_name': 'Lopez',
            'email': 'ana@test.com', 'password1': 'TestPass123!', 'password2': 'TestPass123!'
        })
        self.assertEqual(User.objects.filter(username='nuevo').count(), 1)

    def test_admin_productos_requiere_staff(self):
        self.client.login(username='test_user', password='pass1234')
        r = self.client.get(reverse('admin_productos'))
        self.assertRedirects(r, reverse('menu'))

    def test_admin_puede_ver_productos(self):
        self.client.login(username='admin_user', password='admin1234')
        r = self.client.get(reverse('admin_productos'))
        self.assertEqual(r.status_code, 200)

    def test_crud_crear_producto(self):
        self.client.login(username='admin_user', password='admin1234')
        r = self.client.post(reverse('producto_crear'), {
            'nombre': 'Jugo', 'precio': '4000', 'categoria': self.cat.pk,
            'disponible': True, 'tiempo_preparacion': 3
        })
        self.assertTrue(Producto.objects.filter(nombre='Jugo').exists())

    def test_pago_aprobado(self):
        self.client.login(username='test_user', password='pass1234')
        pedido = Pedido.objects.create(estudiante=self.user, estado='pendiente')
        ItemPedido.objects.create(pedido=pedido, producto=self.producto, cantidad=1)
        pedido.calcular_total()
        r = self.client.post(reverse('pagar', args=[pedido.pk]), {'metodo': 'pse'})
        pedido.refresh_from_db()
        self.assertEqual(pedido.estado, 'en_preparacion')
        self.assertTrue(Pago.objects.filter(pedido=pedido, estado='aprobado').exists())
