from django.db import models
from django.contrib.auth.models import AbstractUser

class TipoUsuario(models.Model):
    TipUsuCod = models.AutoField(primary_key=True)
    TipUsuDes = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.TipUsuDes}'

class Usuario(AbstractUser):
    TipUsuCod = models.ForeignKey(TipoUsuario, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.username

# Modelo para las categorías de los platos
class CategoriaMenu(models.Model):
    CatCod = models.AutoField(primary_key=True)
    CatDes = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.CatDes}'

# Modelo para los estados de los platos
class EstadoMenu(models.Model):
    EstMenCod = models.AutoField(primary_key=True)
    EstMenDes = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.EstMenDes}'

# Modelo para los platos del restaurante
class Menu(models.Model):
    MenCod = models.AutoField(primary_key=True)
    CatCod = models.ForeignKey(CategoriaMenu, on_delete=models.CASCADE)
    EstMenCod = models.ForeignKey(EstadoMenu, on_delete=models.CASCADE)
    MenDes = models.CharField(max_length=255)
    MenImg = models.CharField(max_length=500)
    precio = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)  # Nuevo campo para el precio

    def __str__(self):
        return f'{self.MenDes} (S/. {self.precio:.2f})'  # Mostrar el precio en la representación del objeto

class EstadoMesa(models.Model):
    EstMesCod = models.AutoField(primary_key=True)
    EstMesDes = models.CharField(max_length=100)

    def __str__(self):
        return  f'{self.EstMesDes}'

class Mesa(models.Model):
    numero = models.AutoField(primary_key=True)
    EstMesCod = models.ForeignKey(EstadoMesa, on_delete=models.CASCADE)

    def __str__(self):
        return f"Mesa {self.numero}"

class EstadoPedido(models.Model):
    EstPedCod = models.AutoField(primary_key=True)
    EstPedDes = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.EstPedDes}'

class Pedido(models.Model):
    PedCod = models.AutoField(primary_key=True)
    MesCod = models.ForeignKey(Mesa, on_delete=models.CASCADE)
    MozCod = models.ForeignKey(Usuario, on_delete=models.CASCADE, limit_choices_to={'TipUsuCod__TipUsuDes': 'Mozo'})
    PedCli = models.CharField(max_length=255, blank=True)  # Nombre del cliente
    PedFec = models.DateField()
    PedHor = models.TimeField()
    PedTot = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Inicializa el total en 0
    PedObs = models.TextField(blank=True, default="")  # Valor predeterminado vacío
    EstPedCod = models.ForeignKey(EstadoPedido, on_delete=models.CASCADE)

    def __str__(self):
        return f'Pedido {self.PedCod} - Mesa {self.MesCod}'

class PedidoDetalle(models.Model):
    DetPedCod = models.AutoField(primary_key=True)  # Agregamos un ID para PedidoDetalle
    PedCod = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    MenCod = models.ForeignKey(Menu, on_delete=models.CASCADE)
    PedCan = models.IntegerField()
    PedSub = models.DecimalField(max_digits=10, decimal_places=2)
    PedObs = models.TextField(blank=True)  # Permite observaciones vacías

    class Meta:
        unique_together = (('PedCod', 'MenCod'),)  # Asegura que la combinación de pedido y plato sea única

    def __str__(self):
        return f'Detalle {self.DetPedCod} - {self.MenCod} ({self.PedCan})'
