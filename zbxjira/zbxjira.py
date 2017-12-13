#!/usr/bin/env python
#-*- coding: utf-8 -*-
#-*- coding: iso-8859-1 -*-
#-*- coding: win-1252 -*-


import yaml
from pprint import pprint
from limpar import Limpar
from ticket import Ticket
import argparse
import logging
import sys,os
import re

def main():

    parser = argparse.ArgumentParser(description='Parametros de linha de comando para criar ticket SD no Jira.' +
    'uso padrao: python zbxjira.py -i EVENTO -c CONFIG -o LOG [acao] [resumo] [mensagem] ' +
    'uso basico: python zbxjira.py -i 123456 PROBLEM "Resumo/Titulo do ticket"  "Mensagem/descricao do ticket" ' +
    'uso basico: python zbxjira.py LIMPAR'
    )

    parser.add_argument('-i','--eventid',required=True, help='Id do evento no Zabbix. {EVENT.ID}', type=str)

    parser.add_argument('-c','--config',required=True, help='Caminho do arquivo de configuracao config.yml')

    parser.add_argument('-o','--output',required=True, help='Caminho do arquivo de log')

    parser.add_argument('acao', choices=['PROBLEMA','OK','LIMPAR'], help='Tipo de evento do zabbix.')

    parser.add_argument('resumo', help='Titulo ou sumario do ticket (E utilizado o nome da trigger) {TRIGGER.NAME}.')

    parser.add_argument('mensagem', help='Descricao do ticket. {MESSAGE}')

    opcoes = vars( parser.parse_args())

    #################################################################
    ## Codigo para registro de log
    logging.basicConfig(level=logging.INFO)

    #cria um arquivo para registro dos logs
    #cria diretorio e arquivo caso nao exista
    arq = opcoes['output']

    dir = os.path.dirname(arq)

    if not (os.path.exists(dir)):

        os.makedirs(dir)


    handler = logging.FileHandler(opcoes['output'])

    handler.setLevel(logging.INFO)

    #formata como sera registrado as informacoes no arquivo de log

    #formata como sera registrado as informacoes no arquivo de log
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    handler.setFormatter(formatter)

    #adiciona ao logger o arquivo que ele ira utilizar para fazer os registros

    opcoes['handler'] = handler

    #cria o logger da script
    log = logging.getLogger("zbxjira.main")

    log.addHandler(handler)

    # unknown command
    if not (re.search('(OK|PROBLEMA|LIMPAR)',
            opcoes['acao'],
            re.IGNORECASE)
    ):

        log.critical(
           "zbxjira: acao desconhecida %s" % opcoes['acao'])
        sys.exit(1)

    # default acao (ok/problema/limpar)
    elif (opcoes['acao'] == 'LIMPAR'):

        log.info('Preparando acao de limpeza de arquivos temporarios!')

        limpar = Limpar()

        log.info('Processando acao de %s ' %opcoes['acao'])

        limpar.run()

    else:

        log.info('Estanciando um objeto ticket!')

        ticket = Ticket(opcoes)

        log.info('Processando acao de %s ' %opcoes['acao'])

        ticket.run(opcoes['acao'])



if __name__ == '__main__':

    main()
           
