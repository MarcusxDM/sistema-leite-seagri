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
    # generate_qr_code("2704906")
    nis_list = [23657947783,
    16398911955,
    16574859485,
    20918961194,
    16096589600,
    16096312552,
    20926171660,
    16574565929,
    16574584184,
    16398794983,
    16230551536,
    20048342852,
    16176049947,
    13143160771,
    16244265956,
    16466322069,
    21204218287,
    16304397233,
    16398544944,
    16526179925,
    23679399290,
    16641754651,
    16403651499,
    16001310581,
    16466343627,
    16351316953,
    20919039647,
    20666167812,
    20350025805,
    16451988961,
    16304720336,
    16671158445,
    16053062252,
    16404453046,
    20048342453,
    16325230524,
    16000707895,
    16526488618,
    21232480640,
    16412957201,
    20314251329,
    16377135964,
    20474018142,
    16224968897,
    20928716966,
    22014751543,
    20474017936,
    22017324379,
    16404001889,
    16001038377,
    16350791402,
    16176516154,
    16555415542,
    16650137333,
    16641692184,
    16526328750,
    23699942127,
    16153105441,
    16398478070,
    23722546369,
    16651698401,
    16466314422,
    23744701219,
    16526149732,
    16124831016,
    16389849606,
    16224788422,
    20048342690,
    16205703360,
    16398863438,
    16176288194,
    17056430536,
    16205793394,
    17021999494,
    16398503741,
    23853783305,
    23764718508,
    16574947015,
    16663062930,
    23892037864,
    16089162303,
    12318381862,
    23723628237,
    23878541348,
    23669032041,
    23645991235,
    23667696031,
    23731987038,
    23733820688,
    23681281080,
    23734899865,
    23705704970,
    23688440257,
    20638022074,
    23673806706,
    21214036572,
    23721786129,
    23677596102,
    23705654094,
    23740358277,
    23677820231,
    23744147696,
    23705738522,
    23664892247,
    23720921316,
    16000707895,
    23706314777,
    23718982753,
    23767728997,
    23679260624,
    16095925712,
    23657896585,
    23717697923,
    23671902627,
    23685951382,
    23718903721,
    23674932063,
    23711353033,
    23694776369,
    23742756709,
    23759329620,
    23676409368,
    20926173094,
    23664925757,
    23662135724,
    16582678184,
    23665515471,
    20477618655,
    23690523415,
    16161135338,
    16225233289,
    23681353405,
    23806791356,
    23729035165,
    16001438847,
    23718782339,
    23740590501,
    23741291230,
    23738598282,
    23813058081,
    23784815142,
    16579634570,
    23665632656,
    23643793126,
    23687867605,
    21203109816,
    16421475486]
    
    generate_qr_code(nis_list)
