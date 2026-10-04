from django import forms
from django.utils import timezone

from accounts.forms import BootstrapFormMixin

from .models import Order
from .payments import luhn_is_valid


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


class OrderFilterForm(BootstrapFormMixin, forms.Form):
    q = forms.CharField(
        label='Buscar',
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Nº de pedido, nombre o usuario'}),
    )
    status = forms.ChoiceField(
        label='Estado',
        required=False,
        choices=[('', 'Todos los estados'), *Order.Status.choices],
    )


class OrderStatusForm(forms.Form):
    status = forms.ChoiceField(choices=Order.Status.choices)


class PaymentForm(BootstrapFormMixin, forms.Form):
    card_holder = forms.CharField(
        label='Titular de la tarjeta',
        max_length=100,
        widget=forms.TextInput(attrs={'autocomplete': 'cc-name'}),
    )
    card_number = forms.CharField(
        label='Número de tarjeta',
        max_length=23,
        widget=forms.TextInput(attrs={
            'inputmode': 'numeric',
            'autocomplete': 'cc-number',
            'placeholder': '4242 4242 4242 4242',
        }),
    )
    expiry = forms.CharField(
        label='Caducidad (MM/AA)',
        max_length=5,
        widget=forms.TextInput(attrs={'autocomplete': 'cc-exp', 'placeholder': 'MM/AA'}),
    )
    cvv = forms.CharField(
        label='CVV',
        max_length=4,
        widget=forms.PasswordInput(attrs={'inputmode': 'numeric', 'autocomplete': 'cc-csc'}),
    )

    def clean_card_number(self):
        number = self.cleaned_data['card_number'].replace(' ', '').replace('-', '')
        if not number.isdigit() or not 13 <= len(number) <= 19:
            raise forms.ValidationError('Introduce un número de tarjeta válido.')
        if not luhn_is_valid(number):
            raise forms.ValidationError('El número de tarjeta no es correcto.')
        return number

    def clean_expiry(self):
        value = self.cleaned_data['expiry'].strip()
        try:
            month_text, year_text = value.split('/')
            month, year = int(month_text), 2000 + int(year_text)
        except ValueError:
            raise forms.ValidationError('Usa el formato MM/AA.')
        if not 1 <= month <= 12:
            raise forms.ValidationError('El mes no es válido.')
        today = timezone.localdate()
        if (year, month) < (today.year, today.month):
            raise forms.ValidationError('La tarjeta está caducada.')
        return value

    def clean_cvv(self):
        cvv = self.cleaned_data['cvv'].strip()
        if not cvv.isdigit() or len(cvv) not in (3, 4):
            raise forms.ValidationError('El CVV debe tener 3 o 4 dígitos.')
        return cvv