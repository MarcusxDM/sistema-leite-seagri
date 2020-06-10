from django.db import models
from django.utils import timezone

class Usuario(models.Model):
    nome  = models.CharField(max_length=50)
    email = models.CharField(max_length=100)
    senha = models.CharField(max_length=100)
    admin = models.BooleanField(default=False)
    

class Cooperativa(models.Model):
    nome   = models.CharField(max_length=50)
    membro = models.ManyToManyField(Usuario)

class Transacao(models.Model):
    class Leite(models.TextChoices):
        VACA  = 1, "VACA"
        CABRA = 2, "CABRA"
    litros      = models.FloatField()
    tipo        = models.CharField(max_length=10, choices=Leite.choices, default=Leite.VACA)
    cooperativa = models.ForeignKey(Cooperativa, on_delete=models.CASCADE)
    data        = models.DateField(default=timezone.now)