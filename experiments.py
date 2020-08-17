import csv
import string
import random
import os
import relatorios
from django.core.mail import send_mail


os.environ['DJANGO_SETTINGS_MODULE'] = 'seagri_leite.settings'

import django
django.setup()
def usersAdd(csv_path):
    with open(csv_path, 'r', encoding='utf-8') as csvfile:
        r = csv.reader(csvfile, delimiter=';')
        next(r, None)
        for row in r:
            print(row[0].upper(), row[1], row[2], ''.join(random.choices(string.ascii_uppercase + string.digits, k=7)))
            #try:
            user = relatorios.models.Usuario(nome=row[1], telefone=row[2], email=row[3].replace(' ', ''), senha=(''.join(random.choices(string.ascii_uppercase + string.digits, k=7))),
            ponto_bool=True, cod_ibge=relatorios.models.Localizacao.objects.get(cod_ibge=row[0]))
            user.save()
            print("####### SAVED #######\n")

def coopAtt(csv_path):
    with open(csv_path, 'r', encoding='utf-8') as csvfile:
        r = csv.reader(csvfile, delimiter=';')
        next(r, None)
        for row in r:
            print(row[0], row[1])
            #try:
            ponto = relatorios.models.Ponto(id=row[0])
            ponto.nome = row[1]
            ponto.cnpj = row[2]
            ponto.endereco = row[3]
            ponto.coop = relatorios.models.Cooperativa(id=row[4])
            ponto.cod_ibge = relatorios.models.Localizacao.objects.get(cod_ibge=row[5])
            ponto.save()
            print("####### SAVED #######\n")

def usersCoopAdd(csv_path):
    with open(csv_path, 'r', encoding='utf-8') as csvfile:
        r = csv.reader(csvfile, delimiter=';')
        next(r, None)
        for row in r:
            print(row[0].upper(), row[2], ''.join(random.choices(string.ascii_uppercase + string.digits, k=7)))
            #try:
            user = relatorios.models.Usuario(nome=row[0], email=row[2].replace(' ', ''), senha=(''.join(random.choices(string.ascii_uppercase + string.digits, k=7))),
            coop_bool=True)
            user.save()
            print("####### SAVED #######\n")

def sendEmails():
    usuarios = relatorios.models.Usuario.objects.all()
    for usuario in usuarios:
        send_mail(
        'Sua senha de acesso ao Programa do Leite',
        'Seu email: '+ usuario.email+'\n\n'+'Sua senha: ' + usuario.senha,
        'sic@agricultura.al.gov.br',
        [usuario.email],
        fail_silently=False,
        )



if __name__ == "__main__":
    usersCoopAdd("users_coop.csv")

