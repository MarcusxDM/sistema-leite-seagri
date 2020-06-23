from django.db import models
from django.utils import timezone
from dal import autocomplete
from django import forms

class Leite(models.TextChoices):
        VACA  = 1, "VACA"
        CABRA = 2, "CABRA"

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

class BeneficiarioFinal(models.Model):    
    cpf                 = models.CharField(max_length=11, null=True)
    nome                = models.CharField(max_length=150, null=True)
    nis                 = models.CharField(max_length=11, primary_key=True)
    data_nascimento     = models.DateField(null=True)
    cod_ibge_munic_nasc = models.CharField(max_length=7, null=True)
    identidade          = models.CharField(max_length=20, null=True)

    def __str__(self):
            return self.nis+" | "+self.nome


class Entidade(models.Model):
    nome   = models.CharField(max_length=50)

class Ponto(models.Model):
    nome     = models.CharField(max_length=50)
    membro   = models.ManyToManyField(Usuario)
    entidade = models.ForeignKey(Entidade, on_delete=models.CASCADE)

class Transacao(models.Model):
    litros       = models.FloatField()
    tipo         = models.CharField(max_length=10, choices=Leite.choices, default=Leite.VACA)
    cooperativa  = models.ForeignKey(Cooperativa, on_delete=models.CASCADE)
    data         = models.DateField(default=timezone.now)
    beneficiario = models.ForeignKey(Beneficiario, on_delete=models.CASCADE)


class TransacaoFinal(models.Model):
    litros       = models.FloatField()
    tipo         = models.CharField(max_length=10, choices=Leite.choices, default=Leite.VACA)
    ponto        = models.ForeignKey(Ponto, on_delete=models.CASCADE)
    data         = models.DateField(default=timezone.now)
    beneficiario = models.ForeignKey(BeneficiarioFinal, on_delete=models.CASCADE)