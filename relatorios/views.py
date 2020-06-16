from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import Usuario, Cooperativa, Beneficiario, Transacao
from dal import autocomplete
from .forms import TransacaoProdutor
from django.utils import timezone
from datetime import date, datetime, timedelta
import calendar

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
        print("COTA QUINZENAL ATINGIDA:", litros_disponivel_quin, " Litros")
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
        print("COTA SEMESTRAL ATINGIDA:", litros_disponivel_semestre, " Litros")
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
        print(transacao.litros, " LITROS DE LEITE DE ", transacao.tipo, " ADICIONADOS")
        return redirect(reverse('inserir-transacao-leite'))
    except:
        print("NÃO FOI POSSÍVEL SALVAR TRANSAÇÃO")
        return redirect(reverse('inserir-transacao-leite'))


class BenefiarioAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # validar data_validade__gt=date.today()

        qs = Beneficiario.objects.filter()

        if self.q:
            qs = qs.filter(dap__istartswith=self.q)

        return qs

def index(request):
    return render(request, 'relatorios/index.html', {})

def login(request):
    if request.method == 'POST':
        try:
            user = Usuario.objects.get(email=request.POST['username'])
            if user.senha == request.POST['pass']:
                request.session['login_error'] = ""
                request.session['user_id'] = user.id
                return render(request, 'relatorios/home.html', {'user': user})
            else:
                request.session['login_error'] = 'Senha incorreta'
                return redirect(reverse('index'))
        except:
            request.session['login_error'] = 'Usuário não encontrado'
            return redirect(reverse('index'))
    else:
        return redirect(reverse('index'))

def logout(request):
    request.session.flush()
    return redirect(reverse('index'))
        

def insert_transactions_coop_menu(request):
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

def save_transacao(request):
    if request.method == "POST":
        date_transacao = datetime.strptime(request.POST['data'], '%Y-%m-%d').date()
        produtor = Beneficiario.objects.get(pk=request.POST['beneficiario'])
        if date_transacao <= produtor.data_validade:
                if validate_quinzena(request, date_transacao, produtor):
                    if validate_semestre(request, date_transacao, produtor):
                        transacao_succes(request)
        else:
            print("DAP FORA DE VALIDADE")
    return redirect(reverse('inserir-transacao-leite'))