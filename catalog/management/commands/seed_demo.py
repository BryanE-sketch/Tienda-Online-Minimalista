from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from catalog.models import Category, Product

DEMO_CATALOG = {
    'Deporte': [
        ('Zapatillas de running', 'Ligeras y con buena amortiguación para asfalto.', '89.90', 25),
        ('Camiseta técnica', 'Tejido transpirable de secado rápido.', '24.50', 40),
        ('Mallas de entrenamiento', 'Ajuste cómodo para gimnasio y carrera.', '34.00', 30),
    ],
    'Casual': [
        ('Sudadera con capucha', 'Algodón orgánico, corte amplio.', '49.90', 20),
        ('Pantalón chino', 'Corte recto, para el día a día.', '44.00', 15),
        ('Camisa de lino', 'Fresca y ligera para el verano.', '39.50', 0),
    ],
    'Accesorios': [
        ('Mochila de viaje', 'Capacidad de 30 litros y bolsillo para portátil.', '59.00', 12),
        ('Botella reutilizable', 'Acero inoxidable, 750 ml.', '18.90', 60),
    ],
}


class Command(BaseCommand):
    help = 'Crea categorías y productos de demostración si el catálogo está vacío.'

    @transaction.atomic
    def handle(self, *args, **options):
        if Product.objects.exists():
            self.stdout.write('El catálogo ya tiene productos: no se crea nada.')
            return

        for category_name, products in DEMO_CATALOG.items():
            category, _ = Category.objects.get_or_create(
                slug=slugify(category_name),
                defaults={'name': category_name},
            )
            for name, description, price, stock in products:
                Product.objects.create(
                    category=category,
                    name=name,
                    slug=slugify(name),
                    description=description,
                    price=Decimal(price),
                    stock=stock,
                )

        self.stdout.write(
            self.style.SUCCESS(f'Creados {Product.objects.count()} productos de demostración.')
        )