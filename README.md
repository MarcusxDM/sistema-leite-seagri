# Sistema do Leite


Aplicação Web em Python utilizando framework Django para gerenciamento de transações e criação de relatórios
do programa do leite no estado de Alagoas (PAA Leite).


## Tecnologias


- [Django] - Python Web Application Framework
- [Python 3.7.4]
- [Javascript] 
- [Ajax] 
- [Bootstrap v4] 
- [webcodecamjs] - QR Code reader
- [jQuery]

## Instalação

Instalar dependências de bibliotecas Python atravez do pip:

```sh
pip install -r requirements.txt
```

Adicionar dependências de apps django no settings.py

```python
INSTALLED_APPS = [
    'rangefilter',
    'dal',
    'dal_select2',
    (...)
```

Configurar STMP para envio de e-mails:
```python
# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = 'EMAIL'
EMAIL_HOST_PASSWORD = 'PASSWORD'
SITE = 'LINK DO SITE'
```


**Desenvolvido por Marcus Vinicius Gomes Pestana**
[GitHub]

[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen. Thanks SO - http://stackoverflow.com/questions/4823468/store-comments-in-markdown-syntax)

   [webcodecamjs]: <https://atandrastoth.co.uk/main/pages/plugins/webcodecamjs/>
   [django]: <https://www.djangoproject.com/>
   [Python 3.7.4]: <https://www.python.org/>
   [GitHub]: <https://github.com/MarcusxDM/>
