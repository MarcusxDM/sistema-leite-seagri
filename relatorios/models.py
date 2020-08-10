from django.db import models
from django.utils import timezone
from dal import autocomplete
from django import forms

class Leite(models.TextChoices):
        VACA  = 1, "VACA"
        CABRA = 2, "CABRA"

class Usuario(models.Model):
    nome        = models.CharField(max_length=50)
    email       = models.CharField(max_length=100, unique=True)
    senha       = models.CharField(max_length=100)
    admin       = models.BooleanField(default=False)
    coop_bool   = models.BooleanField(default=False)
    ponto_bool  = models.BooleanField(default=False)
    seagri_bool = models.BooleanField(default=False)

    def __str__(self):
            return self.nome

class Cooperativa(models.Model):
    nome   = models.CharField(max_length=50)
    membro = models.ManyToManyField(Usuario)

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
    cod_ibge_munic_nasc = models.CharField(max_length=7, null=True)
    identidade          = models.CharField(max_length=20, null=True)

    def __str__(self):
            return self.nis+" | "+self.nome


class Entidade(models.Model):
    nome   = models.CharField(max_length=50)

    def __str__(self):
            return self.nome

class Ponto(models.Model):
    nome      = models.CharField(max_length=50)
    membro    = models.ManyToManyField(Usuario)
    entidade  = models.BooleanField(default=False)
    limit_ben = models.IntegerField(default=50)

    def __str__(self):
            return self.nome

class RelatoPonto(models.Model):
    descricao    = models.CharField(max_length=144)
    data         = models.DateField(default=timezone.now)
    ponto        = models.ForeignKey(Ponto, on_delete=models.CASCADE)
    usuario      = models.ForeignKey(Usuario, on_delete=models.CASCADE)

    def __str__(self):
            return  self.data.strftime("%d/%m/%Y") + " | " + self.ponto + " | " + self.descricao

class Transacao(models.Model):
    litros       = models.FloatField()
    tipo         = models.CharField(max_length=10, choices=Leite.choices, default=Leite.VACA)
    cooperativa  = models.ForeignKey(Cooperativa, on_delete=models.CASCADE)
    data         = models.DateField(default=timezone.now)
    beneficiario = models.ForeignKey(Beneficiario, on_delete=models.CASCADE)
    usuario      = models.ForeignKey(Usuario, on_delete=models.CASCADE)

    def __str__(self):
            return self.beneficiario.nome + " | " + self.data.strftime("%d/%m/%Y") + " | " + str(self.litros) + " de " + self.tipo


class TransacaoFinal(models.Model):
    litros       = models.FloatField()
    ponto        = models.ForeignKey(Ponto, on_delete=models.CASCADE)
    data         = models.DateField(default=timezone.now)
    beneficiario = models.ForeignKey(BeneficiarioFinal, on_delete=models.CASCADE)
    usuario      = models.ForeignKey(Usuario, on_delete=models.CASCADE)

    def __str__(self):
            return self.beneficiario.nome + " | " + self.data.strftime("%d/%m/%Y") + " | " + str(self.litros)