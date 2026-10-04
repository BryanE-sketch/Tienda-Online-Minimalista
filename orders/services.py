from django.db import transaction

from catalog.models import Product

from .models import OrderItem


class OrderError(Exception):
    """El pedido no se puede crear; el mensaje se muestra al cliente."""


@transaction.atomic
def create_order(*, user, cart, order):
    """Convierte el carrito en un pedido: todo o nada."""
    if not cart.cart:
        raise OrderError('Tu carrito está vacío.')

    products = (
        Product.objects.available()
        .select_for_update()
        .filter(pk__in=cart.cart.keys())
        .order_by('pk')
    )
    products_by_id = {str(product.pk): product for product in products}

    missing = [product_id for product_id in cart.cart if product_id not in products_by_id]
    if missing:
        for product_id in missing:
            cart.remove(product_id)
        raise OrderError(
            'Algunos productos ya no están disponibles y se han quitado de tu carrito.'
        )

    order.user = user
    order.save()

    for product_id, quantity in cart.cart.items():
        product = products_by_id[product_id]
        if quantity > product.stock:
            raise OrderError(
                f'No hay stock suficiente de «{product.name}»: quedan {product.stock}.'
            )
        OrderItem.objects.create(
            order=order,
            product=product,
            unit_price=product.price,
            quantity=quantity,
        )
        product.stock -= quantity
        product.save(update_fields=['stock', 'updated_at'])

    return order