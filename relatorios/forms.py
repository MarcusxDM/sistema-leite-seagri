from django import forms
from .models import Transacao, TransacaoFinal, Beneficiario, BeneficiarioFinal, Leite
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
    tipo = forms.CharField(
        max_length=10,
        widget=forms.Select(choices=Leite.choices)
    )
    litros       = forms.FloatField()
    #cooperativa  = models.ForeignKey(Cooperativa, on_delete=models.CASCADE)
    data         = forms.DateField()
    beneficiario = forms.ModelChoiceField(queryset=BeneficiarioFinal.objects.all(), widget=autocomplete.ModelSelect2(url='beneficiario-final-autocomplete', attrs={'style' : 'width: 100%'}))

class TransacaoFinalForm(forms.ModelForm):
    class Meta:
        model = TransacaoFinal
        fields = ['litros', 'tipo', 'data', 'beneficiario']