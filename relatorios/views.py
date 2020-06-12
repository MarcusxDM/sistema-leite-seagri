from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import Usuario, Cooperativa

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

def logout(request):
    request.session.flush()
    return redirect(reverse('index'))
        

def insert_transactions_coop_menu(request):
    user = Usuario.objects.get(id=request.session['user_id'])
    coop_list = list(Cooperativa.objects.filter(membro=user))
    
    return render(request, 'relatorios/insert-menu-coop.html', {'user': user, 'coop_list': coop_list})