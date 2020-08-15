from django.db import models
from django.utils import timezone
from dal import autocomplete
from django import forms

class Leite(models.TextChoices):
        VACA  = 1, "VACA"
        CABRA = 2, "CABRA"

class Localizacao(models.Model):
    cod_ibge = models.CharField(max_length=7, primary_key=True)
    uf       = models.CharField(max_length=2)
    municipio = models.CharField(max_length=50)
    def __str__(self):
            return self.municipio

class Usuario(models.Model):
    nome        = models.CharField(max_length=50)
    email       = models.CharField(max_length=100, unique=True)
    senha       = models.CharField(max_length=100)
    admin       = models.BooleanField(default=False)
    coop_bool   = models.BooleanField(default=False)
    ponto_bool  = models.BooleanField(default=False)
    seagri_bool = models.BooleanField(default=False)
    telefone    = models.CharField(max_length=50, default=None, null=True)
    cod_ibge    = models.ForeignKey(Localizacao, on_delete=models.CASCADE, null=True)

    def __str__(self):
            return self.nome

class Cooperativa(models.Model):
    nome     = models.CharField(max_length=150)
    sigla    = models.CharField(max_length=50, null=True)
    cnpj     = models.CharField(max_length=50, null=True)
    responsavel = models.CharField(max_length=50, null=True)
    endereco    = models.CharField(max_length=150, null=True)
    membro   = models.ManyToManyField(Usuario)

    def __str__(self):
            return self.nome

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
    cod_ibge            = models.CharField(max_length=7, null=True)
    identidade          = models.CharField(max_length=20, null=True)

    def __str__(self):
            return self.nis+" | "+self.nome


class Ponto(models.Model):
    nome     = models.CharField(max_length=150)
    membro   = models.ManyToManyField(Usuario)
    coop     = models.ForeignKey(Cooperativa, on_delete=models.CASCADE, null=True)
    cod_ibge = models.ForeignKey(Localizacao, on_delete=models.CASCADE, null=True)
    cnpj     = models.CharField(max_length=50, null=True)
    endereco = models.CharField(max_length=150, null=True)

    def __str__(self):
            return self.cod_ibge.municipio+' | '+self.nome

class Transacao(models.Model):
    litros       = models.FloatField()
    tipo         = models.CharField(max_length=10, choices=Leite.choices, default=Leite.VACA)
    cooperativa  = models.ForeignKey(Cooperativa, on_delete=models.CASCADE)
    data         = models.DateField(default=timezone.now)
    beneficiario = models.ForeignKey(Beneficiario, on_delete=models.CASCADE)

    def __str__(self):
            return self.beneficiario.nome + " | " + self.data.strftime("%d/%m/%Y") + " | " + str(self.litros) + " de " + self.tipo


class TransacaoFinal(models.Model):
    litros       = models.FloatField()
    ponto        = models.ForeignKey(Ponto, on_delete=models.CASCADE)
    data         = models.DateField(default=timezone.now)
    beneficiario = models.ForeignKey(BeneficiarioFinal, on_delete=models.CASCADE)

    def __str__(self):
            return self.beneficiario.nome + " | " + self.data.strftime("%d/%m/%Y") + " | " + str(self.litros)

