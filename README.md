# DeliU — Plataforma de pedidos cafetería universitaria

## Instalación rápida

```bash
pip install -r requirements.txt
python setup_demo.py
python manage.py runserver
```

Abrir http://127.0.0.1:8000/

## Credenciales demo

| Rol | Usuario | Contraseña |
|-----|---------|-----------|
| Admin/Staff | admin | admin123 |

## Tests

```bash
python manage.py test cafeteria
```

## Funcionalidades

- Menú digital con búsqueda y filtro por categoría
- Registro/login de estudiantes
- Carrito de compras con notas
- Pago en línea (simulado) con referencia
- Historial de pedidos del estudiante
- Panel admin personalizado: CRUD de productos (Vistas Genéricas)
- Gestión de pedidos en tiempo real con cambio de estado
- Panel `/admin/` de Django con inline de ítems
- 10 tests unitarios cubriendo modelos, vistas y flujo de pago
