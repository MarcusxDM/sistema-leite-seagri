from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from django.urls import reverse
from .models import Usuario, Cooperativa, Beneficiario, Transacao
from dal import autocomplete
from .forms import TransacaoProdutor
from django.utils import timezone
from datetime import date, datetime, timedelta
import calendar
import csv

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


class BenefiarioAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # validar data_validade__gt=date.today()

        qs = Beneficiario.objects.filter()

        if self.q:
            qs = qs.filter(dap__istartswith=self.q)

        return qs

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

def download_transactions_produtores(request):
    date_inicio = datetime.strptime(request.POST['data-inicio'], '%Y-%m-%d').date()
    date_fim    = datetime.strptime(request.POST['data-fim'], '%Y-%m-%d').date()

    if date_inicio > date_fim:
        d = date_inicio
        date_inicio = date_fim
        date_fim = date_inicio

    output = []
    response = HttpResponse (content_type='text/csv')
    writer = csv.writer(response)
    query_set = Transacao.objects.filter(cooperativa=request.POST['cooperativa'], data__gte=date_inicio, data__lte=date_fim)
    #Header
    writer.writerow(['DAP', 'Enquadramento', 'Categoria', 'Nome', 'UF', 'Munícipio', 'Litros de Leite de Vaca', 'Litros de Leite de Cabra'])
    for user in query_set:
        output.append([user.first_name, user.last_name, user.get_full_name, user.profile.short_name])
    #CSV Data
    writer.writerows(output)
    return response
