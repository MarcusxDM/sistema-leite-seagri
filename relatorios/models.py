from django.db import models
from django.utils import timezone
from dal import autocomplete
from django import forms

class Usuario(models.Model):
    nome  = models.CharField(max_length=50)
    email = models.CharField(max_length=100, unique=True)
    senha = models.CharField(max_length=100)
    admin = models.BooleanField(default=False)
    

class Cooperativa(models.Model):
    nome   = models.CharField(max_length=50)
    membro = models.ManyToManyField(Usuario)

class Beneficiario(models.Model):
    dap           = models.CharField(max_length=25)
    enquadramento = models.CharField(max_length=25)
    categoria     = models.CharField(max_length=50)
    nome          = models.CharField(max_length=150)
    UF            = models.CharField(max_length=2)  
    municipio     = models.CharField(max_length=50)
    data_emissao  = models.DateField()
    data_validade = models.DateField()

    def __str__(self):
            return self.dap+" | "+self.nome

class Transacao(models.Model):
    class Leite(models.TextChoices):
        VACA  = 1, "VACA"
        CABRA = 2, "CABRA"
    litros       = models.FloatField()
    tipo         = models.CharField(max_length=10, choices=Leite.choices, default=Leite.VACA)
    cooperativa  = models.ForeignKey(Cooperativa, on_delete=models.CASCADE)
    data         = models.DateField(default=timezone.now)
    beneficiario = models.ForeignKey(Beneficiario, on_delete=models.CASCADE)
