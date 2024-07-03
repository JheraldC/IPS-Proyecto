from django import forms
from .models import Mesa, Usuario, Menu, PedidoDetalle 

class AbrirMesaForm(forms.ModelForm):
    num_personas = forms.IntegerField(label="# Personas")
    cliente = forms.CharField(label="Cliente")
    mozo = forms.ModelChoiceField(queryset=Usuario.objects.filter(TipUsuCod__TipUsuDes="Mozo"), label="Mozo", empty_label="Selecciona un mozo")
    comentarios = forms.CharField(widget=forms.Textarea, label="Comentarios", required=False)
    numero = forms.IntegerField(widget=forms.HiddenInput()) #Se agrega el campo numero

    class Meta:
        model = Mesa
        fields = ['numero', 'num_personas', 'cliente', 'mozo', 'comentarios']  # Agrega 'numero' a los campos
        from django import forms
