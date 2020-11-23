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
    territorio = models.CharField(max_length=50, null=True, default='')

    def __str__(self):
            return self.municipio

class Usuario(models.Model):
    nome        = models.CharField(max_length=50)
    email       = models.CharField(max_length=100, unique=True)
    senha       = models.CharField(max_length=100)
    admin       = models.BooleanField(default=False)
    coop_bool   = models.BooleanField(default=False)
    ponto_bool  = models.BooleanField(default=False)
    entidade_bool   = models.BooleanField(default=False)
    seagri_bool = models.BooleanField(default=False)
    telefone    = models.CharField(max_length=50, default=None, null=True, blank=True)
    cod_ibge    = models.ForeignKey(Localizacao, on_delete=models.CASCADE, null=True)

    def __str__(self):
            return self.nome

class Cooperativa(models.Model):
    nome     = models.CharField(max_length=150)
    sigla    = models.CharField(max_length=50, null=True)
    cnpj     = models.CharField(max_length=50, null=True)
    responsavel = models.CharField(max_length=50, null=True)
    endereco    = models.CharField(max_length=150, null=True)
    membro      = models.ManyToManyField(Usuario)
    cod_ibge    = models.ForeignKey(Localizacao, on_delete=models.CASCADE, null=True)
    dap         = models.CharField(max_length=50, null=True, default='')

    def __str__(self):
            return self.nome

class Beneficiario(models.Model):
    cpf           = models.CharField(max_length=14, null=True)
    sexo          = models.CharField(max_length=1, null=True, default='')
    dap           = models.CharField(max_length=50, primary_key=True)
    enquadramento = models.CharField(max_length=25)
    categoria     = models.CharField(max_length=50)
    nome          = models.CharField(max_length=150)
    UF            = models.CharField(max_length=2)  
    municipio     = models.CharField(max_length=50)
    data_emissao  = models.DateField()
    data_validade = models.DateField()

    def __str__(self):
            return self.dap+" | "+self.nome

    class Meta:
        verbose_name = "Produtor"
        verbose_name_plural = "Produtores"

class BeneficiarioFinal(models.Model):    
    cpf                 = models.CharField(max_length=11, null=True)
    nome                = models.CharField(max_length=150, null=True)
    nis                 = models.CharField(max_length=11, primary_key=True)
    data_nascimento     = models.DateField(null=True)
    cod_ibge_munic_nasc = models.CharField(max_length=7, null=True)
    identidade          = models.CharField(max_length=20, null=True)
    nome_mae            = models.CharField(max_length=150, null=True)
    faixa_renda         = models.IntegerField()
    data_att            = models.DateField(null=True)

    def __str__(self):
            return self.nis+" | "+self.nome
    
    class Meta:
        verbose_name = "Consumidor"
        verbose_name_plural = "Consumidores"


class Ponto(models.Model):
    nome     = models.CharField(max_length=150)
    membro   = models.ManyToManyField(Usuario, blank=True)
    coop     = models.ForeignKey(Cooperativa, on_delete=models.CASCADE, null=True)
    cod_ibge = models.ForeignKey(Localizacao, on_delete=models.CASCADE, null=True)
    cnpj     = models.CharField(max_length=50, null=True, blank=True)
    endereco = models.CharField(max_length=150, null=True, blank=True)
    limit_beneficiarios = models.IntegerField(null=False, default=0) 

    def __str__(self):
            return self.cod_ibge.municipio+' | '+self.nome

class Transacao(models.Model):
    litros       = models.FloatField()
    tipo         = models.CharField(max_length=10, choices=Leite.choices, default=Leite.VACA)
    cooperativa  = models.ForeignKey(Cooperativa, on_delete=models.CASCADE)
    data         = models.DateField(default=timezone.now)
    beneficiario = models.ForeignKey(Beneficiario, on_delete=models.CASCADE)
    user         = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
            return self.beneficiario.nome + " | " + self.data.strftime("%d/%m/%Y") + " | " + str(self.litros) + " de " + self.tipo + " | " + self.cooperativa.nome
        
    class Meta:
        verbose_name = "Transação Produtor"
        verbose_name_plural = "Transações de Produtores"


class TransacaoFinal(models.Model):
    litros       = models.FloatField()
    ponto        = models.ForeignKey(Ponto, on_delete=models.CASCADE)
    data         = models.DateField(default=timezone.now)
    beneficiario = models.ForeignKey(BeneficiarioFinal, on_delete=models.CASCADE)
    user         = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
            return self.beneficiario.nome + " | " + self.data.strftime("%d/%m/%Y") + " | " + str(self.litros) + " | " + self.ponto.nome + " | " + self.ponto.cod_ibge.municipio
    
    class Meta:
        verbose_name = "Transação Consumidor"
        verbose_name_plural = "Transações para Consumidores"

class Entidade(models.Model):
    cod_ibge = models.ForeignKey(Localizacao, on_delete=models.CASCADE, null=True)
    nome     = models.CharField(max_length=150)
    cnpj     = models.CharField(max_length=50, null=True, blank=True)
    rep_cpf  = models.CharField(max_length=50, null=True, blank=True)
    rep_nome = models.CharField(max_length=150)
    rep_end  = models.CharField(max_length=150,  blank=True)
    rep_tel  = models.CharField(max_length=50)
    rep_email = models.CharField(max_length=150)
    tipo     = models.IntegerField(null=False, default=1)
    coop     = models.ForeignKey(Cooperativa, on_delete=models.CASCADE, null=True) 
    membro   = models.ManyToManyField(Usuario, blank=True)
    
    def __str__(self):
        return self.cod_ibge.municipio+' | '+self.nome

class TransacaoEntidade(models.Model):
    litros      = models.FloatField()
    entidade    = models.ForeignKey(Entidade, on_delete=models.CASCADE)
    data        = models.DateField(default=timezone.now)
    ben_0_6     = models.IntegerField(null=False, default=0)
    ben_7_14    = models.IntegerField(null=False, default=0)
    ben_15_23   = models.IntegerField(null=False, default=0)
    ben_24_65   = models.IntegerField(null=False, default=0)
    ben_66_mais = models.IntegerField(null=False, default=0)
    ben_m       = models.IntegerField(null=False, default=0)
    ben_f       = models.IntegerField(null=False, default=0)
    user        = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=True, blank=True)   

    def __str__(self):
        return self.data.strftime("%d/%m/%Y") + " | " + str(self.litros) + " | " + self.entidade.nome + " | " + self.entidade.cod_ibge.municipio
    
    class Meta:
        verbose_name = "Transação Entidade"
        verbose_name_plural = "Transações de Entidades"

class Laticinio(models.Model):
    cod_ibge = models.ForeignKey(Localizacao, on_delete=models.CASCADE, null=True)
    nome     = models.CharField(max_length=150)
    cnpj     = models.CharField(max_length=50, null=True, blank=True)
    coop     = models.ManyToManyField(Cooperativa, blank=True)

    def __str__(self):
        return self.cod_ibge.municipio+' | '+self.nome