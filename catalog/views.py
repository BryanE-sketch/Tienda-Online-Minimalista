from django.db.models import Q
from django.views.generic import DetailView, ListView

from .forms import ProductFilterForm
from .models import Product


class ProductListView(ListView):
    context_object_name = 'products'
    paginate_by = 6

    def get_queryset(self):
        queryset = Product.objects.available().select_related('category')
        self.form = ProductFilterForm(self.request.GET)

        if self.form.is_valid():
            q = self.form.cleaned_data['q']
            category = self.form.cleaned_data['category']
            order = self.form.cleaned_data['order'] or 'name'

            if q:
                queryset = queryset.filter(
                    Q(name__icontains=q) | Q(description__icontains=q)
                )
            if category:
                queryset = queryset.filter(category=category)
            queryset = queryset.order_by(order, 'pk')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form
        return context


class ProductDetailView(DetailView):
    context_object_name = 'product'

    def get_queryset(self):
        return Product.objects.available().select_related('category')