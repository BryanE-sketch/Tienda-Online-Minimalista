from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView

from catalog.models import Product

from .cart import Cart
from .forms import CartQuantityForm, CheckoutForm, OrderFilterForm, OrderStatusForm
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
    

class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Solo el personal: sin sesión va al acceso; un cliente recibe 403."""

    def test_func(self):
        return self.request.user.is_staff


class ManageOrderListView(StaffRequiredMixin, ListView):
    template_name = 'orders/manage_order_list.html'
    context_object_name = 'orders'
    paginate_by = 10

    def get_queryset(self):
        queryset = Order.objects.with_total().select_related('user')
        self.form = OrderFilterForm(self.request.GET)

        if self.form.is_valid():
            q = self.form.cleaned_data['q']
            status = self.form.cleaned_data['status']

            if q:
                filters = Q(full_name__icontains=q) | Q(user__username__icontains=q)
                if q.isdigit():
                    filters |= Q(pk=int(q))
                queryset = queryset.filter(filters)
            if status:
                queryset = queryset.filter(status=status)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form
        return context


class ManageOrderDetailView(StaffRequiredMixin, DetailView):
    template_name = 'orders/manage_order_detail.html'
    context_object_name = 'order'
    queryset = Order.objects.select_related('user').prefetch_related('items__product')


class ManageOrderStatusView(StaffRequiredMixin, View):
    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        form = OrderStatusForm(request.POST)

        if not form.is_valid():
            messages.error(request, 'El estado no es válido.')
        else:
            try:
                order.change_status(form.cleaned_data['status'])
            except ValidationError as error:
                messages.error(request, error.message)
            else:
                messages.success(
                    request,
                    f'Pedido #{order.pk} marcado como «{order.get_status_display()}».',
                )

        return redirect('orders:manage_order_detail', pk=order.pk)