import csv
import string
import random
import os
import relatorios
from django.core.mail import send_mail
from datetime import datetime, timedelta
import qrcode
import struct
from operator import itemgetter
from pathlib import Path

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


def get_struct_unpacker(fieldspecs, istart, iwidth):
    """
    Build the format string for struct.unpack to use, based on the fieldspecs.
    fieldspecs is a list of [name, start, width] arrays.
    Returns a string like "6s2s3s7x7s4x9s".
    """
    unpack_len = 0
    unpack_fmt = ""
    for fieldspec in fieldspecs:
        start = fieldspec[istart] - 1
        end = start + fieldspec[iwidth]
        if start > unpack_len:
            unpack_fmt += str(start - unpack_len) + "x"
        unpack_fmt += str(end - start) + "s"
        unpack_len = end
    print(unpack_fmt)
    struct_unpacker = struct.Struct(unpack_fmt).unpack_from
    return struct_unpacker

def update_dap_txt(filepath):
    fieldspecs_pessoas = [
        # Name, Start, Width, Type
        ["id", 1, 2, int],
        ["cpf", 3, 13, str],
        ["nome", 14, 83, str],
        ["sexo", 84, 84, str],
        ["mae_nome", 85, 154, str],
        ["apelido", 155, 184, str],
        ["nasc_dta", 185, 192, str],
        ["rg", 193, 204, str],
        ["uf_emissor", 205, 206, str],
        ["nis", 207, 226, str],
        ["uf_nasc", 227, 228, str],
        ["cod_ibge_mun_nasc", 229, 235, str],
        ["cidade_nom", 236, 285, str],
        ["escolaridade", 286, 288, str],
        ["estado_civil", 289, 289, str],
        ["regime_casamento", 290, 290, str],
        ["residencia_local", 291, 291, str],
        ["endereco", 292, 371, str],
        ["endereco_bairro", 372, 421, str],
        ["endereco_numero", 422, 431, str],
        ["residencia_uf", 432, 433, str],
        ["cod_ibge_mun_res", 434, 440, str],
        ["municipio_nome", 441, 490, str],
        ["cep", 491, 500, str],
        ["endereco_princ_bool", 501, 501, str],
        ["cod_ibge_mun_imov_prin", 502, 508, str],
        ["mun_imov_prin_nom", 509, 558, str],
        ["mun_imov_prin_uf", 559, 560, str]
    ]

    fieldspecs = [
        # Name, Start, Width, Type
        ["id", 1, 2, str],
        ["dap_versao", 3, 6, str],
        ["dap", 9, 25, str],
        ["cpf_1", 34, 11, int],
        ["cpf_2", 45, 11, int],
        ["residentes_qntd", 56, 3, int],
        ["categoria", 59, 40, str],
        ["residentes_gerador_qntd", 99, 3, int],
        ["residentes_empregado_perma_qntd", 102, 3, int],
        ["credito_amparo_pronaf_bool", 105, 1, int],
        ["imov_explorados_qntd", 106, 3, int],
        ["imov_prin_nom", 109, 100, str],
        ["imov_prin_local", 209, 150, str],
        ["imov_prin_area", 359, 9, float],
        ["imov_prin_proprietario_bool", 368, 1, int],
        ["enquadramento_final", 369, 3, int],
        ["validade_dta", 372, 8, str],
        ["emissao_dta", 380, 14, str],
        ["insercao_dta", 394, 14, str]
    ]
    iname, istart, iwidth, itype = 0, 1, 2, 3  # field indexes

    fieldspecs.sort(key=itemgetter(istart))
    struct_unpacker = get_struct_unpacker(fieldspecs, istart, iwidth)
    field_indices = range(len(fieldspecs))

    data = []

    for line in Path(filepath).open():
        if line[0:2] == '20':
            print(line.encode())
            raw_fields = struct_unpacker(line.encode())  # split line into field values
            line_data = {}
            for i in field_indices:
                fieldspec = fieldspecs[i]
                fieldname = fieldspec[iname]
                cast = fieldspec[itype]
                print(fieldname, ": ", raw_fields[i])
                value = cast(raw_fields[i].decode().strip())
                line_data[fieldname] = value
            data.append(line_data)
            print(line_data)

    # print(data)


if __name__ == "__main__":
    update_dap_txt('C:/Users/marcus.pestana/Documents/GitHub/bi-seagri-sementes/Fontes/DAPs/arquivo1.txt')
