from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from django.urls import reverse
from .models import Usuario, Cooperativa, Beneficiario, Transacao, Ponto, BeneficiarioFinal, TransacaoFinal
from dal import autocomplete
from .forms import TransacaoProdutor, TransacaoBeneficiarioFinal
from django.utils import timezone
from datetime import date, datetime, timedelta
import calendar
import csv
import pandas as pd
import numpy as np

class BenefiarioAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # validar data_validade__gt=date.today()

        qs = Beneficiario.objects.filter()

        if self.q:
            qs = qs.filter(dap__istartswith=self.q)

        return qs

class BenefiarioFinalAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # validar data_validade__gt=date.today()

        qs = BeneficiarioFinal.objects.filter()

        if self.q:
            qs = qs.filter(nis__istartswith=self.q)

        return qs

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

    if (litros_disponivel_sem > 0) and (float(request.POST['litros']) <= litros_disponivel_sem):
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

    if (litros_disponivel_quin > 0) and (float(request.POST['litros']) <= litros_disponivel_quin):
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

    if (litros_disponivel_semestre > 0) and (float(request.POST['litros']) <= litros_disponivel_semestre):
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
    transacao.litros       = float(request.POST['litros'])
    transacao.tipo         = request.POST['tipo']
    transacao.cooperativa  = Cooperativa.objects.get(pk=request.POST['cooperativa'])
    transacao.data         = request.POST['data']
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
    transacao.litros       = float(request.POST['litros'])
    transacao.tipo         = request.POST['tipo']
    transacao.ponto        = Ponto.objects.get(pk=request.POST['ponto'])
    transacao.data         = request.POST['data']
    try:
        transacao.save()
        request.session['insert_leite_final_error'] = ''
        request.session['insert_leite_final_success'] = ''.join([str(transacao.litros), " LITROS DE LEITE DE ", str(transacao.tipo), " ENTREGUES para ", str(transacao.beneficiario)])
        print(transacao.litros, " LITROS DE LEITE DE ", transacao.tipo, " ENTREGUES")
        return redirect(reverse('inserir-transacaofinal-leite'))
    except:
        request.session['insert_leite_final_success'] = ''
        request.session['insert_leite_final_error'] = "NÃO FOI POSSÍVEL SALVAR A TRANSAÇÃO"
        print(request.session['insert_leite_final_error'])
        return redirect(reverse('inserir-transacaofinal-leite'))

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
        request.session['user_id']
        user = Usuario.objects.get(id=request.session['user_id'])
        if user.admin:
            coop_list = list(Cooperativa.objects.all())
        else:
            coop_list = list(Cooperativa.objects.filter(membro=user))
        form = TransacaoProdutor()
        today = datetime.now().date().strftime('%Y-%m-%d')
        today30 = (datetime.now().date() - timedelta(days=30)).strftime('%Y-%m-%d')
        return render(request, 'relatorios/insert-menu-coop.html', {'user'      : user,
                                                                    'coop_list' : coop_list, 
                                                                    'form'      : form, 
                                                                    'today'     : today, 
                                                                    'today30'   : today30})
    except:
        return redirect(reverse('index'))

def insert_transactions_ponto_menu(request):
    try:
        request.session['user_id']
        user = Usuario.objects.get(id=request.session['user_id'])
        if user.admin:
            ponto_list = list(Ponto.objects.all())
        else:
            ponto_list = list(Ponto.objects.filter(membro=user))
        form = TransacaoBeneficiarioFinal()
        today = datetime.now().date().strftime('%Y-%m-%d')
        today30 = (datetime.now().date() - timedelta(days=30)).strftime('%Y-%m-%d')
        return render(request, 'relatorios/insert-menu-ponto.html', {'user'      : user,
                                                                    'ponto_list' : ponto_list, 
                                                                    'form'      : form, 
                                                                    'today'     : today, 
                                                                    'today30'   : today30})
    except:
        return redirect(reverse('index'))

def save_transacao(request):
    if request.method == "POST":
        request.session['insert_leite_error'] = ""
        date_transacao = datetime.strptime(request.POST['data'], '%Y-%m-%d').date()
        produtor = Beneficiario.objects.get(pk=request.POST['beneficiario'])
        if date_transacao <= produtor.data_validade:
                if validate_quinzena(request, date_transacao, produtor):
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
            transacao_final_succes(request)
        else:
            request.session['insert_leite_final_success'] = ''
            print(request.session['insert_leite_final_error'])
    return redirect(reverse('inserir-transacaofinal-leite'))

def view_transactions_coop_menu(request):
    if request.session['user_id']:
        user = Usuario.objects.get(id=request.session['user_id'])
        if user.admin:
            coop_list = list(Cooperativa.objects.all())
        else:
            coop_list = list(Cooperativa.objects.filter(membro=user))
        today = datetime.now().date().strftime('%Y-%m-%d')
        return render(request, 'relatorios/view-menu-coop.html', {'coop_list' : coop_list, 
                                                                    'today'     : today})
    else:
        return redirect(reverse('index'))

def view_transactions_ponto_menu(request):
    if request.session['user_id']:
        user = Usuario.objects.get(id=request.session['user_id'])
        if user.admin:
            ponto_list = list(Ponto.objects.all())
        else:
            ponto_list = list(Ponto.objects.filter(membro=user))
        today = datetime.now().date().strftime('%Y-%m-%d')
        return render(request, 'relatorios/view-menu-ponto.html', {'ponto_list' : ponto_list, 
                                                                    'today'     : today})
    else:
        return redirect(reverse('index'))

def download_transactions_produtores(request):
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
    writer.writerow(['DAP', 'Enquadramento', 'Categoria', 'Nome', 'UF', 'Munícipio', 'Litros de Leite de Vaca', 'Litros de Leite de Cabra'])

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
                
            output.append([produtor.dap, produtor.enquadramento, produtor.categoria, produtor.nome, produtor.UF, produtor.municipio, str(litros_vaca).replace(".", ","), str(litros_cabra).replace(".", ",")])
        #CSV Data
        writer.writerows(output)
        return response
    else:
        return response
