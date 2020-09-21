from django.contrib import admin
from relatorios.models import *


class UsuarioAdmin(admin.ModelAdmin):
    search_fields = (['nome'])

class PontoAdmin(admin.ModelAdmin):
    search_fields = (['nome', 'cod_ibge__municipio'])

class TransacaoFinalAdmin(admin.ModelAdmin):
    search_fields = (['beneficiario__nome', 'ponto__nome', 'ponto__cod_ibge__municipio'])
    list_filter = (['data'])

class TransacaoAdmin(admin.ModelAdmin):
    search_fields = (['beneficiario__nome', 'cooperativa__nome', 'beneficiario__cod_ibge__municipio'])
    list_filter = (['data'])

admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Cooperativa)
admin.site.register(Ponto, PontoAdmin)
admin.site.register(Transacao, TransacaoAdmin)
admin.site.register(TransacaoFinal, TransacaoFinalAdmin)
admin.site.register(BeneficiarioFinal)
admin.site.register(Entidade)
