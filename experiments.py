import csv
import string
import random
import os
import relatorios
from django.core.mail import send_mail
from datetime import datetime, timedelta
import qrcode

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

def generate_qr_code(nis_list):
    # pontos = relatorios.models.Ponto.objects.filter(cod_ibge=cod_ibge).values_list('pk', flat=True)
    
    # for ponto in pontos:
    #     beneficiarios = ponto.membros_set.all()
    for nis in nis_list:
        try:
            img = qrcode.make(str(nis))
            img.save("C:/Users/marcus.pestana/Documents/Programa do Leite/QR Codes/Mar Vermelho/"+str(nis)+".png")
            print(str(nis)+" GERADO")
        except:
            print(str(nis)+" NÂO GERADO")

if __name__ == "__main__":
   nis_list=[]
   generate_qr_code(nis_list)
