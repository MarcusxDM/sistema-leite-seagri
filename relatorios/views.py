from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from django.urls import reverse
from .models import Usuario, Cooperativa, Beneficiario, Transacao, Ponto, BeneficiarioFinal, TransacaoFinal, Localizacao, TransacaoEntidade, Entidade
from dal import autocomplete
from .forms import TransacaoProdutor, TransacaoBeneficiarioFinal
from django.utils import timezone
from datetime import date, datetime, timedelta
import calendar
import csv
import pandas as pd
import numpy as np
from unicodedata import normalize
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def remover_acentos(txt):
    return normalize('NFKD', txt).encode('ASCII', 'ignore').decode('ASCII')

def getCodIBGE(uf, municipio):
    return Localizacao.objects.get(uf=uf, municipio=remover_acentos(municipio))

class BenefiarioAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # validar data_validade__gt=date.today()

        # qs = Beneficiario.objects.filter()

        # if self.q:
        qs = Beneficiario.objects.filter(dap=self.q)

        return qs

class BenefiarioFinalAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # validar data_validade__gt=date.today()

        # qs = BeneficiarioFinal.objects.filter()

        # if self.q:
        qs = BeneficiarioFinal.objects.filter(nis=self.q, faixa_renda__lte=2)

        return qs

def week_start_end(date):
    start_week = date - timedelta(date.weekday())
    end_week = start_week + timedelta(6)
    return [start_week, end_week]

def load_pontos(request):
    cod_ibge = request.GET.get('cod_ibge')
    
    user = Usuario.objects.get(id=request.session['user_id'])
    if user.admin or user.seagri_bool:
        pontos = Ponto.objects.filter(cod_ibge__cod_ibge=cod_ibge).order_by('nome')
    else:
        pontos = Ponto.objects.filter(cod_ibge__cod_ibge=cod_ibge, membro=user).order_by('nome')
    print(pontos)
    return render(request, 'relatorios/load-pontos.html', {'ponto_list': pontos})

def load_entidades(request):
    cod_ibge = request.GET.get('cod_ibge')
    
    user = Usuario.objects.get(id=request.session['user_id'])
    if user.admin or user.seagri_bool:
        entidades = Entidade.objects.filter(cod_ibge__cod_ibge=cod_ibge).order_by('nome')
    else:
        entidades = Entidade.objects.filter(cod_ibge__cod_ibge=cod_ibge, membro=user).order_by('nome')
    print(entidades, 1)
    return render(request, 'relatorios/load-entidades.html', {'entidade_list': entidades})

def semana_list(date_time):
    first_day_month     = date_time.replace(day=1)
    last_day_month      = first_day_month.replace(month=first_day_month.month+1) - timedelta(days=1)
    half_day_month      = first_day_month + timedelta(days=14)
    afterhalf_day_month = half_day_month + timedelta(days=1)
    
    if (date_time >= first_day_month and date_time <= half_day_month):
        return([first_day_month, half_day_month])
    else:
        return([afterhalf_day_month, last_day_month])

def quinzena_list(date_time):
    first_day_month     = date_time.replace(day=1)
    last_day_month      = first_day_month.replace(month=first_day_month.month+1) - timedelta(days=1)
    half_day_month      = first_day_month + timedelta(days=14)
    afterhalf_day_month = half_day_month + timedelta(days=1)
    
    if (date_time >= first_day_month and date_time <= half_day_month):
        return([first_day_month, half_day_month])
    else:
        return([afterhalf_day_month, last_day_month])

def semestre_list(date_time):
    if date_time >= datetime(date_time.year, 1, 1).date() and date_time < datetime(date_time.year, 7, 1).date():
        first_day_semestre = datetime(date_time.year, 1, 1).date()
        last_day_semestre  = (first_day_semestre.replace(month=7) - timedelta(days=1))
    else:
        first_day_semestre = datetime(date_time.year, 7, 1).date()
        last_day_semestre  = (first_day_semestre.replace(month=1, year=date_time.year+1) - timedelta(days=1))
    return[first_day_semestre, last_day_semestre]

def validate_limit_ben(request, date_transacao, beneficiario):
    month      = date_transacao.month
    ponto      = Ponto.objects.get(pk=request.POST['ponto'])
    transacoes = TransacaoFinal.objects.filter(data__range=week_start_end(date_transacao), ponto__id=request.POST['ponto']).values('beneficiario').distinct()
    is_ben_in  = transacoes.filter(beneficiario=beneficiario).count() > 0
    return (ponto.limit_beneficiarios > transacoes.count() or is_ben_in)


def validate_semana(request, date_transacao, beneficiario_final):
    limit_semanal = 4

    n_dia = calendar.weekday(date_transacao.year, date_transacao.month, date_transacao.day)
    
    if n_dia is 0:
        first_semana_day = date_transacao
        last_semana_day  = date_transacao + timedelta(days=6)

    elif n_dia is 6:
        first_semana_day = date_transacao - timedelta(days=6)
        last_semana_day = date_transacao
    else:
        first_semana_day = date_transacao - timedelta(days=n_dia)
        last_semana_day = date_transacao + timedelta(days=(6 - n_dia))

    consumidor_transacoes_semana = TransacaoFinal.objects.filter(beneficiario=beneficiario_final, data__gte=first_semana_day, data__lte=last_semana_day)
    
    total_litros_semana = 0.0
    for trans in consumidor_transacoes_semana:
        total_litros_semana = trans.litros + total_litros_semana
    
    litros_disponivel_sem = limit_semanal - total_litros_semana

    if (litros_disponivel_sem > 0) and (abs(float(request.POST['litros'])) <= litros_disponivel_sem):
        print("COTA QUINZENAL SEMANAL:", litros_disponivel_sem, " Litros")
        return True
        
    else:
        request.session['insert_leite_final_success'] = ''
        request.session['insert_leite_final_error'] = ''.join(["COTA SEMANAL ATINGIDA: ", str(litros_disponivel_sem), " Litros disponíveis para ", str(beneficiario_final)])
        print(request.session['insert_leite_final_error'])
        return False

def validate_quinzena(request, date_transacao, produtor):
    if request.POST['tipo'] == "VACA":        
                limit_quinzenal = 285
    else:
        limit_quinzenal = 180

    week = quinzena_list(date_transacao)
    first_quinzena_day = week[0]
    last_quinzena_day = week[-1]

    produtor_transacoes_quinzena = Transacao.objects.filter(beneficiario=produtor, data__gte=first_quinzena_day, data__lte=last_quinzena_day, tipo=request.POST['tipo'])
    
    total_litros_quinzena = 0.0
    for trans in produtor_transacoes_quinzena:
        total_litros_quinzena = trans.litros + total_litros_quinzena
    
    litros_disponivel_quin = limit_quinzenal - total_litros_quinzena

    if (litros_disponivel_quin > 0) and (abs(float(request.POST['litros'])) <= litros_disponivel_quin):
        print("COTA QUINZENAL LIBERADA:", litros_disponivel_quin, " Litros")
        return True
        
    else:
        request.session['insert_leite_success'] = ''
        request.session['insert_leite_error'] = ''.join(["COTA QUINZENAL ATINGIDA: ", str(litros_disponivel_quin), " Litros disponíveis para ", str(produtor)])
        print(request.session['insert_leite_error'])
        return False

def validate_semestre(request, date_transacao, produtor):
    if request.POST['tipo'] == "VACA":
        limit_semestral = 3515
    else:
        limit_semestral = 2284 

    semester = semestre_list(date_transacao)
    first_semestre_day = semester[0]
    last_semestre_day = semester[-1]

    produtor_transacoes_semestre = Transacao.objects.filter(beneficiario=produtor, data__gte=first_semestre_day, data__lte=last_semestre_day, tipo=request.POST['tipo'])
    
    total_litros_semestre = 0.0
    for trans in produtor_transacoes_semestre:
        total_litros_semestre = trans.litros + total_litros_semestre
    
    litros_disponivel_semestre = limit_semestral - total_litros_semestre

    if (litros_disponivel_semestre > 0) and (abs(float(request.POST['litros'])) <= litros_disponivel_semestre):
        print("COTA SEMESTRAL LIBERADA:", litros_disponivel_semestre, " Litros")
        return True
        
    else:
        request.session['insert_leite_success'] = ''
        request.session['insert_leite_error'] = ''.join(["COTA SEMESTRAL ATINGIDA: ", str(litros_disponivel_semestre), " Litros disponíveis"])
        print("COTA SEMESTRAL ATINGIDA:", litros_disponivel_semestre, " Litros disponíveis para ", str(produtor))
        return False

def transacao_succes(request):
    transacao = Transacao()
    transacao.beneficiario = Beneficiario.objects.get(pk=request.POST['beneficiario'])
    transacao.litros       = abs(float(request.POST['litros']))
    transacao.tipo         = request.POST['tipo']
    transacao.cooperativa  = Cooperativa.objects.get(pk=request.POST['cooperativa'])
    transacao.data         = request.POST['data']
    transacao.user         = Usuario.objects.get(pk=request.session['user_id'])
    try:
        transacao.save()
        request.session['insert_leite_error'] = ''
        request.session['insert_leite_success'] = ''.join([str(transacao.litros), " LITROS DE LEITE DE ", str(transacao.tipo), " ADICIONADOS para ", str(transacao.beneficiario)])
        print(transacao.litros, " LITROS DE LEITE DE ", transacao.tipo, " ADICIONADOS")
        return redirect(reverse('inserir-transacao-leite'))
    except:
        request.session['insert_leite_success'] = ''
        request.session['insert_leite_error'] = "NÃO FOI POSSÍVEL SALVAR A TRANSAÇÃO"
        print(request.session['insert_leite_error'])
        return redirect(reverse('inserir-transacao-leite'))

def transacao_final_succes(request):
    transacao              = TransacaoFinal()
    transacao.beneficiario = BeneficiarioFinal.objects.get(pk=request.POST['beneficiario'])
    transacao.litros       = abs(float(request.POST['litros']))
    transacao.ponto        = Ponto.objects.get(pk=request.POST['ponto'])
    transacao.data         = request.POST['data']
    transacao.user         = Usuario.objects.get(pk=request.session['user_id'])
    try:
        transacao.save()
        request.session['insert_leite_final_error'] = ''
        request.session['insert_leite_final_success'] = ''.join([str(transacao.litros), " LITROS DE LEITE ENTREGUES para ", str(transacao.beneficiario)])
        print(transacao.litros, " LITROS DE LEITE ENTREGUES")
        return redirect(reverse('inserir-transacaofinal-leite'))
    except:
        request.session['insert_leite_final_success'] = ''
        request.session['insert_leite_final_error'] = "NÃO FOI POSSÍVEL SALVAR A TRANSAÇÃO"
        print(request.session['insert_leite_final_error'])
        return redirect(reverse('inserir-transacaofinal-leite'))

def save_transacao_entidade(request):
    if request.method == 'POST':
        transacao             = TransacaoEntidade()
        transacao.litros      = abs(float(request.POST['litros']))
        transacao.data        = request.POST['data']
        transacao.entidade    = Entidade.objects.get(pk=request.POST['entidade'])
        transacao.ben_0_6     = request.POST['ben_0_6']
        transacao.ben_7_14    = request.POST['ben_7_14']
        transacao.ben_15_23   = request.POST['ben_15_23']
        transacao.ben_24_65   = request.POST['ben_24_65']
        transacao.ben_66_mais = request.POST['ben_66_mais']
        transacao.ben_m       = request.POST['ben_m']
        transacao.ben_f       = request.POST['ben_f']
        transacao.user        = Usuario.objects.get(pk=request.session['user_id'])
        try:
            transacao.save()
            request.session['insert_leite_final_error'] = ''
            request.session['insert_leite_final_success'] = ''.join([str(transacao.litros), " LITROS DE LEITE ENTREGUES"])
            print(transacao.litros, " LITROS DE LEITE ENTREGUES")
        except:
            request.session['insert_leite_final_success'] = ''
            request.session['insert_leite_final_error'] = "NÃO FOI POSSÍVEL SALVAR A TRANSAÇÃO"
            print(request.session['insert_leite_final_error'])
    return redirect(reverse('inserir-transacao-entidade-leite'))

def index(request):
    request.session.flush()
    return render(request, 'relatorios/index.html', {})

def login(request):
    if request.method == 'POST':
        try:
            user = Usuario.objects.get(email=request.POST['username'])
            if user.senha == request.POST['pass']:
                request.session['login_error'] = ""
                request.session['user_id'] = user.id
                request.session['coop_bool'] = user.coop_bool
                request.session['ponto_bool'] = user.ponto_bool
                request.session['admin'] = user.admin
                request.session['seagri_bool'] = user.seagri_bool
                request.session['entidade_bool'] = user.entidade_bool
                return redirect('home')
            else:
                request.session['login_error'] = 'Senha incorreta'
                return redirect(reverse('index'))
        except:
            request.session['login_error'] = 'Usuário não encontrado'
            return redirect(reverse('index'))
    else:
        return redirect(reverse('index'))

def home(request):
    try:
        request.session['user_id']
        return render(request, 'relatorios/home.html')
    except:
        return redirect(reverse('index'))

def logout(request):
    request.session.flush()
    return redirect(reverse('index'))
        

def insert_transactions_coop_menu(request):
    try:
        if(request.session['coop_bool'] or request.session['admin']):
            user = Usuario.objects.get(id=request.session['user_id'])
            if user.admin:
                coop_list = list(Cooperativa.objects.all().order_by('nome'))
            else:
                coop_list = list(Cooperativa.objects.filter(membro=user).order_by('nome'))
            form = TransacaoProdutor()
            today = datetime.now().date().strftime('%Y-%m-%d')
            today30 = (datetime.now().date() - timedelta(days=90)).strftime('%Y-%m-%d')
            return render(request, 'relatorios/insert-menu-coop.html', {'user'      : user,
                                                                        'coop_list' : coop_list, 
                                                                        'form'      : form, 
                                                                        'today'     : today, 
                                                                        'today30'   : today30})
        else:
            return redirect(reverse('index'))
    except:
        return redirect(reverse('index'))

def insert_transactions_ponto_menu(request):
    try:
        if(request.session['ponto_bool'] or request.session['admin']):
            user = Usuario.objects.get(id=request.session['user_id'])
            if user.admin:
                ponto_list = list(Ponto.objects.all().order_by('nome'))
            else:
                ponto_list = list(Ponto.objects.filter(membro=user).order_by('nome'))
            form = TransacaoBeneficiarioFinal()
            today = datetime.now().date().strftime('%Y-%m-%d')
            today30 = (datetime.now().date() - timedelta(days=90)).strftime('%Y-%m-%d')
            return render(request, 'relatorios/insert-menu-ponto.html', {'user'      : user,
                                                                        'ponto_list' : ponto_list, 
                                                                        'form'      : form, 
                                                                        'today'     : today, 
                                                                        'today30'   : today30})
        else:
            return redirect(reverse('index'))
    except:
        return redirect(reverse('index'))

def insert_transactions_entidade_menu(request):
    try:
        if(request.session['entidade_bool'] or request.session['admin']):
            user = Usuario.objects.get(id=request.session['user_id'])
            if user.admin:
                entidade_list = list(Entidade.objects.all().order_by('nome'))
            else:
                entidade_list = list(Entidade.objects.filter(membro=user).order_by('nome'))
            today = datetime.now().date().strftime('%Y-%m-%d')
            today30 = (datetime.now().date() - timedelta(days=90)).strftime('%Y-%m-%d')
            return render(request, 'relatorios/insert-menu-entidade.html', {'user'      : user,
                                                                            'entidade_list' : entidade_list, 
                                                                            'today'     : today, 
                                                                            'today30'   : today30})
        else:
            return redirect(reverse('index'))
    except:
        return redirect(reverse('index'))

def save_transacao(request):
    if request.method == "POST":
        request.session['insert_leite_error'] = ""
        date_transacao = datetime.strptime(request.POST['data'], '%Y-%m-%d').date()
        produtor = Beneficiario.objects.get(pk=request.POST['beneficiario'])
        if date_transacao <= produtor.data_validade:
                if validate_semestre(request, date_transacao, produtor):
                    transacao_succes(request)
        else:
            request.session['insert_leite_success'] = ''
            request.session['insert_leite_error'] = "DAP FORA DE VALIDADE"
            print(request.session['insert_leite_error'])
    return redirect(reverse('inserir-transacao-leite'))

def save_transacao_ponto(request):
    if request.method == "POST":
        request.session['insert_leite_final_error'] = ""
        date_transacao = datetime.strptime(request.POST['data'], '%Y-%m-%d').date()
        beneficiario = BeneficiarioFinal.objects.get(pk=request.POST['beneficiario'])
        if validate_semana(request, date_transacao, beneficiario):
            if (validate_limit_ben(request, date_transacao, beneficiario)):
                transacao_final_succes(request)
            else:
                request.session['insert_leite_final_success'] = ''
                request.session['insert_leite_final_error'] = 'ESTE PONTO JÁ ENTREGOU AO NÚMERO MÁXIMO DE CONSUMIDORES'
        else:
            request.session['insert_leite_final_success'] = ''
            print(request.session['insert_leite_final_error'])
    return redirect(reverse('inserir-transacaofinal-leite'))

def view_transactions_coop_menu(request):
    try:
        if(request.session['coop_bool'] or request.session['seagri_bool'] or request.session['admin']):
            user = Usuario.objects.get(id=request.session['user_id'])
            if user.admin or user.seagri_bool:
                coop_list = list(Cooperativa.objects.all())
            else:
                coop_list = list(Cooperativa.objects.filter(membro=user))
            today = datetime.now().date().strftime('%Y-%m-%d')
            return render(request, 'relatorios/view-menu-coop.html', {'coop_list' : coop_list, 
                                                                        'today'     : today})
        else:
            return redirect(reverse('index'))
    except:
        return redirect(reverse('index'))


def view_transactions_ponto_menu(request):
    #try:
        if (request.session['ponto_bool'] or request.session['seagri_bool'] or request.session['admin']):
            user = Usuario.objects.get(id=request.session['user_id'])
            if user.admin or user.seagri_bool:
                municipio_list = list(Localizacao.objects.filter(cod_ibge__startswith='27'))
                municipio_all = True
            else:
                ponto_list = list(Ponto.objects.filter(membro=user))
                municipio_list = set([p.cod_ibge for p in ponto_list])
                municipio_all = False
            ponto_list = []
            today = datetime.now().date().strftime('%Y-%m-%d')
            return render(request, 'relatorios/view-menu-ponto.html', {'ponto_list' : ponto_list, 
                                                                        'today'     : today,
                                                                        'municipio_list' : municipio_list,
                                                                        'municipio_all' : municipio_all})
        else:
            return redirect(reverse('index'))
    #except:
        return redirect(reverse('index'))

def view_transactions_entidade_menu(request):
    #try:
        if (request.session['entidade_bool'] or request.session['seagri_bool'] or request.session['admin']):
            user = Usuario.objects.get(id=request.session['user_id'])
            if user.admin or user.seagri_bool:
                municipio_list = list(Localizacao.objects.filter(cod_ibge__startswith='27'))
                municipio_all = True
            else:
                entidade_list = list(Entidade.objects.filter(membro=user))
                municipio_list = set([p.cod_ibge for p in entidade_list])
                municipio_all = False
            entidade_list = []
            today = datetime.now().date().strftime('%Y-%m-%d')
            return render(request, 'relatorios/view-menu-entidade.html', {'entidade_list' : entidade_list, 
                                                                        'today'     : today,
                                                                        'municipio_list' : municipio_list,
                                                                        'municipio_all' : municipio_all})
        else:
            return redirect(reverse('index'))
    #except:
        return redirect(reverse('index'))

def download_transactions_produtores(request):
    if request.method == "POST":
        date_inicio = datetime.strptime(request.POST['data-inicio'], '%Y-%m-%d').date()
        date_fim    = datetime.strptime(request.POST['data-fim'], '%Y-%m-%d').date()

        if date_inicio > date_fim:
            d = date_inicio
            date_inicio = date_fim
            date_fim = date_inicio

        output = []
        response = HttpResponse (content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="Leite_Produtores_"'+str(date_inicio)+"-"+str(date_fim)+".csv"
        writer = csv.writer(response, delimiter=";")
        #Header
        writer.writerow(['UF', 'CÓD. IBGE COM 7 DIGITOS', 'MUNICÍPIO', 'NOME DO PRODUTOR', 'C. P. F.', 'Nº DA DAP',
        	'TIPO DE DAP',	'ENQUADRAMENTO NO GRUPO DO PRONAF', 'NOME DA ORGANIZAÇÃO PRODUTORA', 
            'Litros de Leite de Vaca', 'Litros de Leite de Cabra'])

        # Get Coop
        coop = Cooperativa.objects.get(id=request.POST['cooperativa'])
        print(coop)

        # Grouping by Produtor
        query_set = Transacao.objects.filter(cooperativa=request.POST['cooperativa'], data__gte=date_inicio, data__lte=date_fim)
        if query_set:
            df = pd.DataFrame.from_records(query_set.values())
            sf = df.groupby(['beneficiario_id', 'tipo'])['litros'].sum()
            df = sf.to_frame().reset_index()

            df = pd.pivot_table(df, values='litros', index=['beneficiario_id'], columns=['tipo'], fill_value=0)
            df_dict = df.to_dict('index')

            for key, value in df_dict.items():
                produtor = Beneficiario.objects.get(pk=key)

                try:
                    value['VACA']
                    litros_vaca = value['VACA']
                except:
                    litros_vaca = 0
                
                try:
                    value['CABRA']
                    litros_cabra = value['CABRA']
                except:
                    litros_cabra = 0
                
                prod_local = getCodIBGE(produtor.UF, produtor.municipio)

                if not produtor.cpf:
                    produtor.cpf = "000.000.000-00"
                output.append([produtor.UF, prod_local.cod_ibge, produtor.municipio, produtor.nome, produtor.cpf, produtor.dap, produtor.categoria, produtor.enquadramento,
                            coop.sigla, str(litros_vaca).replace(".", ","), str(litros_cabra).replace(".", ",")])
            #CSV Data
            writer.writerows(output)
            return response
        else:
            return response
    return redirect(reverse('visualizar-transacao-leite'))

def download_transactions_consumidores(request):
    if request.method == "POST":
        date_inicio = datetime.strptime(request.POST['data-inicio'], '%Y-%m-%d').date()
        date_fim    = datetime.strptime(request.POST['data-fim'], '%Y-%m-%d').date()

        if date_inicio > date_fim:
            d = date_inicio
            date_inicio = date_fim
            date_fim = date_inicio

        output = []
        response = HttpResponse (content_type='text/csv;')
        response['Content-Disposition'] = 'attachment; filename="Leite_Consumidores_"'+str(date_inicio)+"-"+str(date_fim)+".csv"
        writer = csv.writer(response, delimiter=";")
        #Header
        writer.writerow(['UF', 'CÓD. IBGE com 7 digitos', 'MUNICÍPIO', 'Nome do Beneficíario', 'Data de Nascimento','Nome da Mãe',
                         'C. P. F  BENEFICIÁRIO', 'NIS', 'Ponto de Distribuição', 'COOPERATIVA', 'Litros de Leite'])

        if request.POST['action'] == "PONTO":
            # Ponto
            ponto = Ponto.objects.get(id=request.POST['ponto'])

            # Grouping by Produtor
            query_set = TransacaoFinal.objects.filter(ponto=request.POST['ponto'], data__gte=date_inicio, data__lte=date_fim)
            if query_set:
                df = pd.DataFrame.from_records(query_set.values())
                sf = df.groupby(['beneficiario_id'])['litros'].sum()
                df = sf.to_frame().reset_index()

                df = pd.pivot_table(df, values='litros', index=['beneficiario_id'], fill_value=0)
                df_dict = df.to_dict('index')

                for key, value in df_dict.items():
                    consumidor = BeneficiarioFinal.objects.get(pk=key)
                    if not consumidor.cpf:
                            consumidor.cpf = '00000000000'
                    output.append([ponto.cod_ibge.uf, ponto.cod_ibge.cod_ibge, ponto.cod_ibge.municipio, consumidor.nome, consumidor.data_nascimento, consumidor.nome_mae,
                                (consumidor.cpf[0:3]+'.'+consumidor.cpf[3:6]+'.'+consumidor.cpf[6:9]+'-'+consumidor.cpf[9:]), consumidor.nis,
                                ponto.nome, ponto.coop.sigla, str(value['litros']).replace(".", ",")])
                #CSV Data
                writer.writerows(output)
                return response
            else:
                return response
        else:
            # Pontos
            pontos_id = TransacaoFinal.objects.filter(data__gte=date_inicio, data__lte=date_fim).distinct().values_list('ponto_id')
            pontos = Ponto.objects.filter(id__in=pontos_id)
            for ponto in pontos:
                output = []
                # Grouping by Produtor
                query_set = TransacaoFinal.objects.filter(ponto=ponto, data__gte=date_inicio, data__lte=date_fim)
                # print(query_set)
                if query_set:
                    df = pd.DataFrame.from_records(query_set.values())
                    sf = df.groupby(['beneficiario_id'])['litros'].sum()
                    
                    df = sf.to_frame().reset_index()
                    
                    df = pd.pivot_table(df, values='litros', index=['beneficiario_id'], fill_value=0)
                    
                    df_dict = df.to_dict('index')
                    for key, value in df_dict.items():
                        consumidor = BeneficiarioFinal.objects.get(pk=key)
                        if not consumidor.cpf:
                            consumidor.cpf = '00000000000'
                        output.append([ponto.cod_ibge.uf, ponto.cod_ibge.cod_ibge, ponto.cod_ibge.municipio, consumidor.nome, consumidor.data_nascimento, consumidor.nome_mae,
                                    (consumidor.cpf[0:3]+'.'+consumidor.cpf[3:6]+'.'+consumidor.cpf[6:9]+'-'+consumidor.cpf[9:]), consumidor.nis,
                                    ponto.nome, ponto.coop.sigla, str(value['litros']).replace(".", ",")])
                    #CSV Data
                    writer.writerows(output)
            return response
    return redirect(reverse('visualizar-transacaofinal-leite'))

def download_transactions_entidades(request):
    if request.method == "POST":
        date_inicio = datetime.strptime(request.POST['data-inicio'], '%Y-%m-%d').date()
        date_fim    = datetime.strptime(request.POST['data-fim'], '%Y-%m-%d').date()

        if date_inicio > date_fim:
            d = date_inicio
            date_inicio = date_fim
            date_fim = date_inicio

        output = []
        response = HttpResponse (content_type='text/csv;')
        response['Content-Disposition'] = 'attachment; filename="Leite_Entidade_"'+str(date_inicio)+"-"+str(date_fim)+".csv"
        writer = csv.writer(response, delimiter=";")
        #Header
        writer.writerow(['UF', 'CÓD. IBGE COM 7 DIGITOS', 'MUNICÍPIO', 'NOME DA ENTIDADE','CNPJ',
                    'NOME DO REPRESENTANTE', 'C. P. F',	'TELEFONE',	'ENDEREÇO',	'E-MAIL', 'IDENTIFICAÇÃO DA ENTIDADE',
                    'COOPERATIVA',	'0 - 6 anos',	'7 - 14 anos',	'15 - 23 anos',	'24 - 65 anos',	'Acima de 65 anos',
                    'M', 'F', 'QUANTIDADE DE LITROS'])

        if request.POST['action'] == "ENTIDADE":
            # Entidade
            entidade = Entidade.objects.get(id=request.POST['entidade'])

            # Grouping by Entidade
            query_set = TransacaoEntidade.objects.filter(entidade=request.POST['entidade'], data__gte=date_inicio, data__lte=date_fim)
            if query_set:
                df = pd.DataFrame.from_records(query_set.values())
                sf = df.groupby(['entidade_id'])[['ben_0_6', 'ben_7_14', 'ben_15_23', 'ben_24_65', 'ben_66_mais', 'ben_m', 'ben_f', 'litros']].sum()
                df = sf.reset_index()
                
                df = pd.pivot_table(df, values=['ben_0_6', 'ben_7_14', 'ben_15_23', 'ben_24_65', 'ben_66_mais', 'ben_m', 'ben_f', 'litros'], index=['entidade_id'], fill_value=0)
                df_dict = df.to_dict('index')
                
                for key, value in df_dict.items():
                    output.append([entidade.cod_ibge.uf, entidade.cod_ibge.cod_ibge, entidade.cod_ibge.municipio, entidade.nome, entidade.cnpj, entidade.rep_nome,
                                (entidade.rep_cpf[0:3]+'.'+entidade.rep_cpf[3:6]+'.'+entidade.rep_cpf[6:9]+'-'+entidade.rep_cpf[9:]), entidade.rep_tel,
                                entidade.rep_end, entidade.rep_email, entidade.tipo, entidade.coop.sigla, value['ben_0_6'], value['ben_7_14'], value['ben_15_23'],
                                value['ben_24_65'], value['ben_66_mais'], value['ben_m'], value['ben_f'],str(value['litros']).replace(".", ",")])
                #CSV Data
                writer.writerows(output)
                return response
            else:
                return response
        else:

            query_set = TransacaoEntidade.objects.filter(data__gte=date_inicio, data__lte=date_fim)
            if query_set:
                df = pd.DataFrame.from_records(query_set.values())
                sf = df.groupby(['entidade_id'])[['ben_0_6', 'ben_7_14', 'ben_15_23', 'ben_24_65', 'ben_66_mais', 'ben_m', 'ben_f', 'litros']].sum()
                df = sf.reset_index()
                
                df = pd.pivot_table(df, values=['ben_0_6', 'ben_7_14', 'ben_15_23', 'ben_24_65', 'ben_66_mais', 'ben_m', 'ben_f', 'litros'], index=['entidade_id'], fill_value=0)
                df_dict = df.to_dict('index')
                
                for key, value in df_dict.items():
                    entidade = Entidade.objects.get(id=key)
                    output.append([entidade.cod_ibge.uf, entidade.cod_ibge.cod_ibge, entidade.cod_ibge.municipio, entidade.nome, entidade.cnpj, entidade.rep_nome,
                                (entidade.rep_cpf[0:3]+'.'+entidade.rep_cpf[3:6]+'.'+entidade.rep_cpf[6:9]+'-'+entidade.rep_cpf[9:]), entidade.rep_tel,
                                entidade.rep_end, entidade.rep_email, entidade.tipo, entidade.coop.sigla, value['ben_0_6'], value['ben_7_14'], value['ben_15_23'],
                                value['ben_24_65'], value['ben_66_mais'], value['ben_m'], value['ben_f'],str(value['litros']).replace(".", ",")])
                #CSV Data
                writer.writerows(output)
            return response
    return redirect(reverse('visualizar-transacao-entidade-leite'))

def last_beneficiarios(request):
    ponto_id = request.GET.get('ponto')
    ben_ids = TransacaoFinal.objects.filter(data__range=week_start_end(datetime.now() - timedelta(7)), ponto__id=ponto_id).values_list('beneficiario').distinct()
    ben_ids_this_week = TransacaoFinal.objects.filter(data__range=week_start_end(datetime.now()), ponto__id=ponto_id).values_list('beneficiario').distinct()

    ben_ids = [x[0] for x in ben_ids] 
    ben_ids_this_week = [x[0] for x in ben_ids_this_week]
    history_ben = set(ben_ids) - set(ben_ids_this_week)
    ben_query = BeneficiarioFinal.objects.filter(nis__in=history_ben)
    
    return render(request, 'relatorios/last-beneficiarios.html', {'beneficiarios_list': ben_query})

def load_transacoes(request):
    date_search = datetime.strptime(request.GET['data-search'], '%Y-%m-%d').date()
    transacao_list = TransacaoFinal.objects.select_related('beneficiario').filter(ponto_id=request.GET['ponto'], data=date_search)
    page = request.GET.get('page', 1)
    paginator = Paginator(transacao_list, 10)
    try:
        transacoes = paginator.page(page)
    except PageNotAnInteger:
        transacoes = paginator.page(1)
    except EmptyPage:
        transacoes = paginator.page(paginator.num_pages)

    return render(request, 'relatorios/load-transacoes-ponto.html', { 'transacoes': transacoes })

def manage_transactions_ponto_menu(request):
    try:
        if (request.session['ponto_bool'] or request.session['seagri_bool'] or request.session['admin']):
            user = Usuario.objects.get(id=request.session['user_id'])
            if user.admin or user.seagri_bool:
                municipio_list = list(Localizacao.objects.filter(cod_ibge__startswith='27'))
                municipio_all = True
            else:
                ponto_list = list(Ponto.objects.filter(membro=user))
                municipio_list = set([p.cod_ibge for p in ponto_list])
                municipio_all = False
            ponto_list = []
            today = datetime.now().date().strftime('%Y-%m-%d')
            return render(request, 'relatorios/manage-menu-ponto.html', {'ponto_list' : ponto_list, 
                                                                        'today'     : today,
                                                                        'municipio_list' : municipio_list,
                                                                        'municipio_all' : municipio_all})
        else:
            return redirect(reverse('index'))
    except:
        return redirect(reverse('index'))

def delete_transacao_ponto(request):
    if request.method == "POST":
        transacao = TransacaoFinal.objects.get(pk=request.POST['transacao'])
        transacao.delete()
    return render(request, 'relatorios/load-transacoes-ponto.html')
        