# Tienda Online Minimalista

E-commerce básico desarrollado con Django, sin pasarela de pago real.
Proyecto 2 del módulo de Django.

===============================================================================================
Usuario	  /  Contraseña	 /   Permisos
-----------------------------------------------------------------------------------------------
Profesor /	ConquerX	/   Uso completo del inventario (sin acceso al panel de administración)
===============================================================================================

**Demo:** https://tienda-bryan.onrender.com

El plan gratuito de Render suspende el servicio tras 15 minutos sin uso,
así que la primera carga puede tardar cerca de un minuto.

## Funcionalidades

**Obligatorias**

- Listado de productos con búsqueda, filtro por categoría, orden y paginación.
- Detalle de producto.
- Carrito en la sesión: añadir, cambiar cantidad y quitar.
- Creación de pedidos con transacción, precio congelado y descuento de stock.
- Panel para que el personal gestione los pedidos y sus estados.

**Extras**

- Carga de imágenes de producto (Cloudinary en producción).
- Pasarela de pago simulada con validación de tarjeta.

## Cómo probar la demo

1. Crea una cuenta desde "Crear cuenta".
2. Añade productos al carrito y finaliza la compra.
3. Paga con una tarjeta de prueba (caducidad futura y cualquier CVV):
   - `4242 4242 4242 4242`: pago aprobado.
   - `4000 0000 0000 0002`: pago rechazado.
4. Consulta el pedido en "Mis pedidos".

El panel de gestión (`/gestion/pedidos/`) requiere una cuenta de personal.

## Tecnologías

- Python 3.12 y Django 6.1
- Bootstrap 5
- SQLite en desarrollo y PostgreSQL en producción
- Gunicorn, WhiteNoise y Cloudinary
- Despliegue en Render

## Estructura

| App | Responsabilidad |
|---|---|
| `accounts` | Usuario personalizado, registro y acceso |
| `catalog` | Categorías, productos e imágenes |
| `orders` | Carrito, pedidos, pago simulado y panel de gestión |


## Instalación en local

```bash
git clone https://github.com/BryanE-sketch/Tienda-Online-Minimalista.git
cd Tienda-Online-Minimalista
conda create -n tienda-env python=3.12.11 -y
conda activate tienda-env
pip install -r requirements.txt
cp .env.example .env
```

Edita `.env` y rellena `SECRET_KEY`. Después:

```bash
python manage.py migrate
python manage.py seed_demo
python manage.py createsuperuser
python manage.py runserver
```