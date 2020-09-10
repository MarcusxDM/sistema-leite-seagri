from django import forms
from .models import Transacao, TransacaoFinal, Beneficiario, BeneficiarioFinal, Leite, TransacaoEntidade
from dal import autocomplete

class TransacaoProdutor(forms.Form):
    tipo = forms.CharField(
        max_length=10,
        widget=forms.Select(choices=Leite.choices)
    )
    litros       = forms.FloatField()
    #cooperativa  = models.ForeignKey(Cooperativa, on_delete=models.CASCADE)
    data         = forms.DateField()
    beneficiario = forms.ModelChoiceField(queryset=Beneficiario.objects.all(), widget=autocomplete.ModelSelect2(url='beneficiario-autocomplete', attrs={'style' : 'width: 100%'}))

class TransacaoForm(forms.ModelForm):
    class Meta:
        model = Transacao
        fields = ['litros', 'tipo', 'data', 'beneficiario']

class TransacaoBeneficiarioFinal(forms.Form):
    litros       = forms.FloatField()
    #cooperativa  = models.ForeignKey(Cooperativa, on_delete=models.CASCADE)
    data         = forms.DateField()
    beneficiario = forms.ModelChoiceField(queryset=BeneficiarioFinal.objects.all(), widget=autocomplete.ModelSelect2(url='beneficiario-final-autocomplete', attrs={'style' : 'width: 100%'}))

class TransacaoFinalForm(forms.ModelForm):
    class Meta:
        model = TransacaoFinal
        fields = ['litros', 'data', 'beneficiario']

class TransacaoEntidadeFinal(forms.Form):
    litros      = forms.FloatField()
    data        = forms.DateField()
    ben_0_6     = forms.IntegerField()
    ben_7_14    = forms.IntegerField()
    ben_15_23   = forms.IntegerField()
    ben_24_65   = forms.IntegerField()
    ben_66_mais = forms.IntegerField()
    ben_m       = forms.IntegerField()
    ben_f       = forms.IntegerField()

class TransacaoEntidadeForm(forms.ModelForm):
    class Meta:
        model = TransacaoEntidade
        fields = ['litros', 'data', 'ben_0_6', 'ben_7_14', 'ben_15_23', 'ben_24_65', 'ben_66_mais', 'ben_m', 'ben_f']