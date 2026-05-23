"""
Script de configuración inicial: crea migraciones, superusuario y datos de demo.
Ejecutar una sola vez después de instalar dependencias.

Uso: python setup_demo.py
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deliu.settings')

# Asegurarse de estar en el directorio del proyecto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

from django.core.management import call_command
from django.contrib.auth.models import User

print("⚙️  Creando migraciones...")
call_command('makemigrations', 'cafeteria')
call_command('migrate')

print("👤 Creando superusuario admin / admin123...")
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@deliu.co', 'admin123')

print("🥗 Cargando datos de demo...")
from cafeteria.models import Categoria, Producto

cats = {
    'Bebidas': Categoria.objects.get_or_create(nombre='Bebidas')[0],
    'Comidas': Categoria.objects.get_or_create(nombre='Comidas')[0],
    'Snacks': Categoria.objects.get_or_create(nombre='Snacks')[0],
}

productos = [
    ('Café americano', 'Café negro recién preparado', 2500, 'Bebidas', 3),
    ('Jugo natural de naranja', 'Naranja recién exprimida 400ml', 4000, 'Bebidas', 5),
    ('Agua 600ml', 'Agua mineral con o sin gas', 1500, 'Bebidas', 1),
    ('Arepa con queso', 'Arepa de maíz rellena de queso blanco', 4500, 'Comidas', 8),
    ('Bandeja ejecutiva', 'Arroz, proteína, ensalada y jugo', 12000, 'Comidas', 15),
    ('Sándwich de pollo', 'Pan artesanal, pollo a la plancha, tomate y lechuga', 7500, 'Comidas', 10),
    ('Empanada de pipián', 'Empanada frita rellena de pipián', 2000, 'Snacks', 5),
    ('Chocoramo', 'Ponqué bañado en chocolate', 1800, 'Snacks', 1),
    ('Granola con yogur', 'Yogur natural con granola y frutos rojos', 5500, 'Snacks', 4),
]

for nombre, desc, precio, cat, tiempo in productos:
    Producto.objects.get_or_create(
        nombre=nombre,
        defaults={'descripcion': desc, 'precio': precio, 'categoria': cats[cat], 'tiempo_preparacion': tiempo}
    )

print("\n✅ Listo. Ejecuta: python manage.py runserver")
print("   Admin:     http://127.0.0.1:8000/admin/   (admin / admin123)")
print("   App:       http://127.0.0.1:8000/")
