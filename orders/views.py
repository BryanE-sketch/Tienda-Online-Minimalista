from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView

from catalog.models import Product

from .cart import Cart
from .forms import CartQuantityForm, CheckoutForm
from .models import Order
from .services import OrderError, create_order


def cart_detail(request):
    return render(request, 'orders/cart_detail.html')


def _apply_quantity(request, product, requested):
    """Guarda la cantidad pedida y avisa si el stock obligó a reducirla."""
    final = Cart(request).set_quantity(product, requested)
    if final == 0:
        messages.error(request, f'«{product.name}» está agotado.')
    elif final < requested:
        messages.warning(
            request,
            f'Solo quedan {product.stock} unidades de «{product.name}»; '
            'hemos ajustado tu carrito.',
        )
    else:
        messages.success(request, f'Carrito actualizado: {final} x «{product.name}».')


@require_POST
def cart_add(request, product_id):
    product = get_object_or_404(Product.objects.available(), pk=product_id)
    form = CartQuantityForm(request.POST)
    if not form.is_valid():
        messages.error(request, 'La cantidad no es válida.')
        return redirect(product)

    requested = Cart(request).quantity_of(product) + form.cleaned_data['quantity']
    _apply_quantity(request, product, requested)
    return redirect('orders:cart_detail')


@require_POST
def cart_update(request, product_id):
    product = get_object_or_404(Product.objects.available(), pk=product_id)
    form = CartQuantityForm(request.POST)
    if not form.is_valid():
        messages.error(request, 'La cantidad no es válida.')
    else:
        _apply_quantity(request, product, form.cleaned_data['quantity'])
    return redirect('orders:cart_detail')


@require_POST
def cart_remove(request, product_id):
    Cart(request).remove(product_id)
    messages.success(request, 'Producto eliminado del carrito.')
    return redirect('orders:cart_detail')


@login_required
def checkout(request):
    cart = Cart(request)
    if not cart.lines:
        messages.warning(request, 'Tu carrito está vacío.')
        return redirect('orders:cart_detail')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            try:
                order = create_order(
                    user=request.user,
                    cart=cart,
                    order=form.save(commit=False),
                )
            except OrderError as error:
                messages.error(request, str(error))
                return redirect('orders:cart_detail')

            cart.clear()
            messages.success(request, f'¡Gracias! Hemos recibido tu pedido #{order.pk}.')
            return redirect(order)
    else:
        form = CheckoutForm()

    return render(request, 'orders/checkout.html', {'form': form})


class OrderListView(LoginRequiredMixin, ListView):
    context_object_name = 'orders'
    paginate_by = 10

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items')


class OrderDetailView(LoginRequiredMixin, DetailView):
    context_object_name = 'order'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items__product')