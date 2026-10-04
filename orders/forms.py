from django import forms

from accounts.forms import BootstrapFormMixin

from .models import Order


class CartQuantityForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, max_value=99)


class CheckoutForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Order
        fields = ['full_name', 'address', 'city', 'postal_code']

    def clean_postal_code(self):
        postal_code = self.cleaned_data['postal_code'].strip()
        if not (postal_code.isdigit() and len(postal_code) == 5):
            raise forms.ValidationError('El código postal debe tener 5 dígitos.')
        return postal_code