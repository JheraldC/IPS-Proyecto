from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Mesa, Usuario, Menu, CategoriaMenu, EstadoMesa

class BaseForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})  # Aplicar la clase form-control a todos los campos

class AbrirMesaForm(BaseForm):
    num_personas = forms.IntegerField(label="# Personas")
    cliente = forms.CharField(label="Cliente")
    mozo = forms.ModelChoiceField(queryset=Usuario.objects.filter(TipUsuCod__TipUsuDes="Mozo"), label="Mozo", empty_label="Selecciona un mozo")
    comentarios = forms.CharField(widget=forms.Textarea, label="Comentarios", required=False)
    numero = forms.IntegerField(widget=forms.HiddenInput())

    class Meta:
        model = Mesa
        fields = ['numero', 'num_personas', 'cliente', 'mozo', 'comentarios']

class MenuForm(BaseForm):
    class Meta:
        model = Menu
        fields = '__all__'
        labels = {
            'CatCod': 'Categoría',
            'EstMenCod': 'Estado',
            'MenDes': 'Nombre del Plato',
            'MenImg': 'Imagen del Plato',
            'precio': 'Precio',
        }
        widgets = {
            'MenImg': forms.FileInput(attrs={'class': 'form-control'}),
        }

class CategoriaMenuForm(BaseForm):
    class Meta:
        model = CategoriaMenu
        fields = ['CatDes']
        labels = {
            'CatDes': 'Nombre de la categoría'
        }

class MesaForm(BaseForm):
    class Meta:
        model = Mesa
        fields = ['EstMesCod']
        labels = {
            'EstMesCod': 'Estado de la Mesa',
        }

class CustomUserCreationForm(BaseForm, UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = UserCreationForm.Meta.fields + ('TipUsuCod',)
        labels = {
            'TipUsuCod': 'Tipo de Usuario',
        }

class CustomUserChangeForm(UserChangeForm):
    password = forms.CharField(widget=forms.PasswordInput, required=True, label='Contraseña')  # Label para contraseña

    class Meta(UserChangeForm.Meta):
        model = Usuario
        fields = ('username', 'first_name', 'last_name', 'email', 'password', 'TipUsuCod')
        labels = {
            'username': 'Nombre de usuario',
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Correo electrónico',
            'TipUsuCod': 'Tipo de Usuario',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})  # Aplicar la clase form-control a todos los campos
        self.fields['username'].required = True

