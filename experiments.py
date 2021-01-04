import csv
import string
import random
import os
import relatorios
from django.core.mail import send_mail
from datetime import datetime, timedelta

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
        try:
            send_mail(
            'Sua senha de acesso ao Programa do Leite',
            'Seu email: '+ usuario.email+'\n\n'+'Sua senha: ' + usuario.senha,
            'marcusvpestana@gmail.com',
            [usuario.email],
            fail_silently=False,
            )
            print("######### ENVIADO para "+usuario.email+" #########\n")
        except:
            print("######### ERRO "+usuario.email+" #########\n")

def updateDap(csv_path):
    with open(csv_path, 'r', encoding='utf-8') as csvfile:
        r = csv.reader(csvfile, delimiter=';')
        next(r, None)
        for row in r:
            if (row[5] == 'AL'):
                print("\nPRODUTOR:\n")
                print(row[0], row[1], row[2], row[3], row[5], row[6], row[7], row[8])

                produtor, created = relatorios.models.Beneficiario.objects.update_or_create(
                                                            dap=row[0],
                                                            defaults={
                                                                'enquadramento': row[1],
                                                                'categoria'    : row[2],
                                                                'nome'         : row[3],
                                                                'UF'           : row[5],
                                                                'municipio'    : row[6],
                                                                'data_emissao' : datetime.strptime(row[7], '%d/%m/%Y').date(),
                                                                'data_validade': datetime.strptime(row[8], '%d/%m/%Y').date() 
                                                                },
                                                            )
                if created:
                    print("################## CREATED ##################")
                else:
                    print("################## UPDATED ##################")

if __name__ == "__main__":
    # updateDap('dap/cafdapativa.csv')
    pass
