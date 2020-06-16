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
    # print(first_day_month, half_day_month, afterhalf_day_month, last_day_month)
    
    if (date_time >= first_day_month and date_time <= half_day_month):
        return([first_day_month, half_day_month])
    else:
        return([afterhalf_day_month, last_day_month])



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
    return render(request, 'relatorios/insert-menu-coop.html', {'user': user, 'coop_list': coop_list, 'form':form})

def save_transacao(request):
    if request.method == "POST":
        date_transacao = datetime.strptime(request.POST['data'], '%Y-%m-%d').date()
        produtor = Beneficiario.objects.get(pk=request.POST['beneficiario'])
        if date_transacao <= produtor.data_validade:        

            produtor_transacoes = Transacao.objects.filter(beneficiario=produtor)

            week = quinzena_list(date_transacao)
            first_quinzena_day = week[0]
            last_quinzena_day = week[-1]

            transacoes_quinzena = produtor_transacoes.filter(data__gte=first_quinzena_day, data__lte=last_quinzena_day)
            total_litros_quinzena = 0.0
            for trans in transacoes_quinzena:
                total_litros_quinzena = trans.litros + total_litros_quinzena
            
            litros_disponivel_quin = 285 - total_litros_quinzena

            if (litros_disponivel_quin > 0) and (float(request.POST['litros']) <= litros_disponivel_quin):
                transacao = Transacao()
            
                transacao.beneficiario = Beneficiario.objects.get(pk=request.POST['beneficiario'])
                transacao.litros       = float(request.POST['litros'])
                transacao.tipo         = request.POST['tipo']
                transacao.cooperativa  = Cooperativa.objects.get(pk=request.POST['cooperativa'])
                transacao.data         = request.POST['data']
                try:
                    transacao.save()
                    return redirect(reverse('inserir-transacao-leite'))
                except:
                    print("NÃO FOI POSSÍVEL SALVAR TRANSAÇÃO")
                    return redirect(reverse('inserir-transacao-leite'))
            else:
                print("COTA QUINZENAL ATINGIDA:", litros_disponivel_quin, " Litros")
                return redirect(reverse('inserir-transacao-leite'))
        else:
            print("DAP FORA DE VALIDADE")
            return redirect(reverse('inserir-transacao-leite'))
    else:
        return redirect(reverse('inserir-transacao-leite'))