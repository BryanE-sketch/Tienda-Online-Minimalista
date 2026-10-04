from django import forms

from .models import Category


class ProductFilterForm(forms.Form):
    ORDER_CHOICES = [
        ('name', 'Nombre'),
        ('price', 'Precio: de menor a mayor'),
        ('-price', 'Precio: de mayor a menor'),
        ('-created_at', 'Novedades'),
    ]

    q = forms.CharField(
        label='Buscar',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar productos...',
        }),
    )
    category = forms.ModelChoiceField(
        label='Categoría',
        queryset=Category.objects.all(),
        required=False,
        to_field_name='slug',
        empty_label='Todas las categorías',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    order = forms.ChoiceField(
        label='Ordenar por',
        choices=ORDER_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )