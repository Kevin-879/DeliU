from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Pedido, ItemPedido, Pago, Producto
import uuid


class RegistroForm(UserCreationForm):
    TIPO_CHOICES = [
        ('normal', 'Usuario normal'),
        ('admin', 'Administrador'),
    ]
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=50, label="Nombre")
    last_name = forms.CharField(max_length=50, label="Apellido")
    tipo = forms.ChoiceField(choices=TIPO_CHOICES, label="Tipo de cuenta", widget=forms.RadioSelect)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'tipo']


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio', 'categoria', 'disponible', 'tiempo_preparacion']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }


class AgregarItemForm(forms.Form):
    producto_id = forms.IntegerField(widget=forms.HiddenInput)
    cantidad = forms.IntegerField(min_value=1, max_value=10, initial=1)


class PagoForm(forms.ModelForm):
    class Meta:
        model = Pago
        fields = ['metodo']
        labels = {'metodo': 'Método de pago'}

    def save(self, commit=True):
        pago = super().save(commit=False)
        pago.referencia = str(uuid.uuid4())[:12].upper()
        pago.estado = 'aprobado'
        if commit:
            pago.save()
        return pago


class PedidoNotasForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['notas']
        widgets = {'notas': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Instrucciones especiales...'})}
        labels = {'notas': 'Notas del pedido'}


class ActualizarEstadoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['estado']
        labels = {'estado': 'Estado'}
