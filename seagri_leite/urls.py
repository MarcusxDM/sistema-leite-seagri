"""seagri_leite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from relatorios import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('home/', views.home, name='home'),
    path('login-success/', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('inserir-transacao-leite/', views.insert_transactions_coop_menu, name='inserir-transacao-leite'),
    path('save-transacao/', views.save_transacao, name='save-transacao'),
    path('save-transacao-ponto/', views.save_transacao_ponto, name='save-transacao-ponto'),
    path('save-transacao-entidade/', views.save_transacao_entidade, name='save-transacao-entidade'),
    path('beneficiario-autocomplete/', views.BenefiarioAutocomplete.as_view(), name='beneficiario-autocomplete'),
    path('beneficiario-final-autocomplete/', views.BenefiarioFinalAutocomplete.as_view(), name='beneficiario-final-autocomplete'),
    path('visualizar-transacao-leite/', views.view_transactions_coop_menu, name='visualizar-transacao-leite'),
    path('inserir-transacaofinal-leite/', views.insert_transactions_ponto_menu, name='inserir-transacaofinal-leite'),
    path('visualizar-transacaofinal-leite/', views.view_transactions_ponto_menu, name='visualizar-transacaofinal-leite'),
    path('visualizar-transacao-leite/', views.view_transactions_coop_menu, name='visualizar-transacao-leite'),
    path('inserir-transacao-entidade-leite/', views.insert_transactions_entidade_menu, name='inserir-transacao-entidade-leite'),
    path('visualizar-transacao-entidade-leite/', views.view_transactions_entidade_menu, name='visualizar-transacao-entidade-leite'),
    path('download-consumidores/', views.download_transactions_consumidores, name='download-consumidores'),
    path('download-produtores/', views.download_transactions_produtores, name='download-produtores'),
    path('download-entidades/', views.download_transactions_entidades, name='download-entidades'),
    path('ajax/load-pontos/', views.load_pontos, name='ajax_load_pontos'),
    path('ajax/load-entidades/', views.load_entidades, name='ajax_load_entidades')
    
]
