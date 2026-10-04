from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse


class Category(models.Model):
    name = models.CharField('nombre', max_length=100, unique=True)
    slug = models.SlugField('slug', max_length=120, unique=True)

    class Meta:
        verbose_name = 'categoría'
        verbose_name_plural = 'categorías'
        ordering = ['name']

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        """Productos visibles en la tienda pública."""
        return self.filter(is_active=True)


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products',
        verbose_name='categoría',
    )
    name = models.CharField('nombre', max_length=200)
    slug = models.SlugField('slug', max_length=220, unique=True)
    description = models.TextField('descripción', blank=True)
    price = models.DecimalField(
        'precio',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
    )
    stock = models.PositiveIntegerField('stock', default=0)
    is_active = models.BooleanField('activo', default=True)
    created_at = models.DateTimeField('creado', auto_now_add=True)
    updated_at = models.DateTimeField('actualizado', auto_now=True)

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'producto'
        verbose_name_plural = 'productos'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('catalog:product_detail', kwargs={'slug': self.slug})