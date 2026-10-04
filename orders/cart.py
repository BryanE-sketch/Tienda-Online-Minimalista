from django.utils.functional import cached_property

from catalog.models import Product

CART_SESSION_KEY = 'cart'


class Cart:
    """Carrito guardado en la sesión como {id de producto: cantidad}."""

    def __init__(self, request):
        self.session = request.session
        self.cart = self.session.get(CART_SESSION_KEY, {})

    def __len__(self):
        return sum(self.cart.values())

    def quantity_of(self, product):
        return self.cart.get(str(product.pk), 0)

    def set_quantity(self, product, quantity):
        """Fija la cantidad sin superar el stock y devuelve la cantidad final."""
        quantity = min(quantity, product.stock)
        if quantity > 0:
            self.cart[str(product.pk)] = quantity
        else:
            self.cart.pop(str(product.pk), None)
        self.save()
        return quantity

    def remove(self, product_id):
        self.cart.pop(str(product_id), None)
        self.save()

    def clear(self):
        self.cart = {}
        self.save()

    def save(self):
        self.session[CART_SESSION_KEY] = self.cart
        self.__dict__.pop('lines', None)

    @cached_property
    def lines(self):
        products = Product.objects.available().filter(pk__in=self.cart.keys())
        return [
            {
                'product': product,
                'quantity': self.cart[str(product.pk)],
                'subtotal': product.price * self.cart[str(product.pk)],
            }
            for product in products
        ]

    @property
    def total(self):
        return sum(line['subtotal'] for line in self.lines)