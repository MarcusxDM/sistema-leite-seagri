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
        for row in r:
            print(row[0].upper(), row[1], row[2], ''.join(random.choices(string.ascii_uppercase + string.digits, k=7)))
            try:
                user = relatorios.models.Usuario(nome=row[0].upper(), telefone=row[1], email=row[2], senha=(''.join(random.choices(string.ascii_uppercase + string.digits, k=7))), ponto_bool=True,
                ponto=relatorios.models.Ponto.objects.get(nome=row['ponto'], cod_ibge=row['cod_ibge']))
                user.save()
                print("####### SAVED #######")
            except:
                print("####### ERROR #######")
            
            

def sendEmails():
    # usuarios = relatorios.models.Usuario.objects.all()
    usuarios = relatorios.models.Usuario.objects.filter(nome='marcus')
    for usuario in usuarios:
        send_mail(
        'Sua senha de acesso ao Programa do Leite',
        'Seu email: '+ usuario.email+'\n\n'+'Sua senha: ' + usuario.senha,
        'marcusvpestana@gmail.com',
        [usuario.email],
        fail_silently=False,
        )



if __name__ == "__main__":
    # usersAdd("PLANILHA SISTEMA - PONTOS - COORDENADORES - RESPONSÁVEIS.csv")
    sendEmails()
