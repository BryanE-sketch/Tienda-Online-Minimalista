from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.db.models import F, Sum
from django.urls import reverse

from catalog.models import Product


class OrderQuerySet(models.QuerySet):
    def with_total(self):
        """Añade total_amount calculado en la base de datos."""
        return self.annotate(
            total_amount=Sum(
                F('items__unit_price') * F('items__quantity'),
                output_field=models.DecimalField(max_digits=12, decimal_places=2),
            )
        )


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pendiente'
        PAID = 'paid', 'Pagado'
        SHIPPED = 'shipped', 'Enviado'
        DELIVERED = 'delivered', 'Entregado'
        CANCELLED = 'cancelled', 'Cancelado'

    ALLOWED_TRANSITIONS = {
        Status.PENDING: [Status.PAID, Status.CANCELLED],
        Status.PAID: [Status.SHIPPED, Status.CANCELLED],
        Status.SHIPPED: [Status.DELIVERED],
        Status.DELIVERED: [],
        Status.CANCELLED: [],
    }
    STATUS_COLORS = {
        Status.PENDING: 'warning',
        Status.PAID: 'info',
        Status.SHIPPED: 'primary',
        Status.DELIVERED: 'success',
        Status.CANCELLED: 'secondary',
    }

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='orders',
        verbose_name='cliente',
    )
    status = models.CharField(
        'estado',
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    full_name = models.CharField('nombre completo', max_length=150)
    address = models.CharField('dirección', max_length=250)
    city = models.CharField('ciudad', max_length=100)
    postal_code = models.CharField('código postal', max_length=10)
    created_at = models.DateTimeField('creado', auto_now_add=True)
    updated_at = models.DateTimeField('actualizado', auto_now=True)

    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'pedido'
        verbose_name_plural = 'pedidos'
        ordering = ['-created_at']

    def __str__(self):
        return f'Pedido #{self.pk}'

    def get_absolute_url(self):
        return reverse('orders:order_detail', kwargs={'pk': self.pk})

    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())

    @property
    def next_statuses(self):
        return self.ALLOWED_TRANSITIONS[self.status]

    @property
    def status_color(self):
        return self.STATUS_COLORS[self.status]

    @transaction.atomic
    def change_status(self, new_status):
        """Cambia el estado si la transición es válida; al cancelar devuelve el stock."""
        current = Order.objects.select_for_update().get(pk=self.pk)
        if new_status not in self.ALLOWED_TRANSITIONS[current.status]:
            raise ValidationError(
                f'Un pedido «{current.get_status_display()}» no puede pasar a '
                f'«{self.Status(new_status).label}».'
            )

        if new_status == self.Status.CANCELLED:
            for item in current.items.all():
                Product.objects.filter(pk=item.product_id).update(
                    stock=F('stock') + item.quantity
                )

        self.status = new_status
        self.save(update_fields=['status', 'updated_at'])


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='pedido',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='order_items',
        verbose_name='producto',
    )
    unit_price = models.DecimalField(
        'precio unitario',
        max_digits=10,
        decimal_places=2,
    )
    quantity = models.PositiveIntegerField(
        'cantidad',
        validators=[MinValueValidator(1)],
    )

    class Meta:
        verbose_name = 'línea de pedido'
        verbose_name_plural = 'líneas de pedido'
        constraints = [
            models.UniqueConstraint(
                fields=['order', 'product'],
                name='unique_product_per_order',
            ),
        ]

    def __str__(self):
        return f'{self.quantity} x {self.product}'

    @property
    def subtotal(self):
        return self.unit_price * self.quantity