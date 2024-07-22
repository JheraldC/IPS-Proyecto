from django import forms
from .models import Mesa, Usuario, Menu, CategoriaMenu, EstadoMesa

class AbrirMesaForm(forms.ModelForm):
    num_personas = forms.IntegerField(label="# Personas")
    cliente = forms.CharField(label="Cliente")
    mozo = forms.ModelChoiceField(queryset=Usuario.objects.filter(TipUsuCod__TipUsuDes="Mozo"), label="Mozo", empty_label="Selecciona un mozo")
    comentarios = forms.CharField(widget=forms.Textarea, label="Comentarios", required=False)
    numero = forms.IntegerField(widget=forms.HiddenInput()) #Se agrega el campo numero

    class Meta:
        model = Mesa
        fields = ['numero', 'num_personas', 'cliente', 'mozo', 'comentarios']  # Agrega 'numero' a los campos

class MenuForm(forms.ModelForm):
    class Meta:
        model = Menu
        fields = '__all__'  # O especifica los campos que quieres incluir

class CategoriaMenuForm(forms.ModelForm):
    class Meta:
        model = CategoriaMenu
        fields = ['CatDes']  # Incluye el campo CatDes (nombre de la categoría)
        labels = {
            'CatDes': 'Nombre de la categoría'  # Personaliza la etiqueta del campo
        }
        widgets = {
            'CatDes': forms.TextInput(attrs={'class': 'form-control'})  # Personaliza el widget del campo
        }

class MesaForm(forms.ModelForm):
    class Meta:
        model = Mesa
        fields = ['numero', 'EstMesCod']  # Incluye los campos necesarios
        labels = {
            'numero': 'Número de Mesa',
            'EstMesCod': 'Estado de la Mesa',
        }
        widgets = {
            'numero': forms.NumberInput(attrs={'class': 'form-control'}),
            'EstMesCod': forms.Select(attrs={'class': 'form-control'}),
        }

