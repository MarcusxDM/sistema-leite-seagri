from django.contrib import admin
from relatorios.models import *
from rangefilter.filter import DateRangeFilter


class UsuarioAdmin(admin.ModelAdmin):
    search_fields = (['nome'])

class CooperativaAdmin(admin.ModelAdmin):
    list_display = (['cod_ibge', 'nome'])
    list_display_links = (['nome'])
    search_fields = (['nome', 'cod_ibge__municipio'])
    filter_horizontal = (['membro'])

class PontoAdmin(admin.ModelAdmin):
    list_display = (['cod_ibge', 'nome'])
    list_display_links = (['nome'])
    search_fields = (['nome', 'cod_ibge__municipio'])
    filter_horizontal = (['membro'])

class EntidadeAdmin(admin.ModelAdmin):
    list_display = (['cod_ibge', 'nome'])
    list_display_links = (['nome'])
    search_fields = (['nome', 'cod_ibge__municipio'])
    filter_horizontal = (['membro'])

class TransacaoFinalAdmin(admin.ModelAdmin):
    search_fields = (['beneficiario__nis', 'beneficiario__nome', 'ponto__nome', 'ponto__cod_ibge__municipio'])
    list_filter = ([('data', DateRangeFilter)])

class TransacaoAdmin(admin.ModelAdmin):
    search_fields = (['beneficiario__dap', 'beneficiario__nome', 'cooperativa__nome', 'beneficiario__municipio', 'cooperativa__sigla'])
    list_filter = ([('data', DateRangeFilter)])

class TransacaoEntidadeAdmin(admin.ModelAdmin):
    search_fields = (['entidade__nome', 'entidade__cod_ibge__municipio'])
    list_filter = ([('data', DateRangeFilter)])

class BeneficiarioFinalAdmin(admin.ModelAdmin):
    list_display = (['nis', 'nome', 'data_att'])
    list_display_links = (['nis', 'nome'])
    search_fields = (['nome', 'nis', 'cod_ibge_munic_nasc'])
    list_filter = ([('data_att', DateRangeFilter)])

class BeneficiarioAdmin(admin.ModelAdmin):
    search_fields = (['nome', 'dap', 'UF', 'municipio'])

admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Cooperativa, CooperativaAdmin)
admin.site.register(Ponto, PontoAdmin)
admin.site.register(Transacao, TransacaoAdmin)
admin.site.register(TransacaoFinal, TransacaoFinalAdmin)
admin.site.register(BeneficiarioFinal, BeneficiarioFinalAdmin)
admin.site.register(Beneficiario, BeneficiarioAdmin)
admin.site.register(Entidade, EntidadeAdmin)
admin.site.register(TransacaoEntidade, TransacaoEntidadeAdmin)