import jira
from zabbix_api import ZabbixAPI
from zabbix_api import *
import yaml
import logging
import os

class Base(object):
    """Classe base."""
########################################################################
    def __init__(self, opcoes, *args, **kwargs):
        
        self.opcoes = opcoes
        
        self.args = args
        
        self.kwargs = kwargs
        
        self.log = logging.getLogger("zbxjira.base")
        
        self.log.addHandler(opcoes['handler'])

        try:
        
             with open(opcoes['config'], 'r') as c:
        
               self.conf = yaml.load(c)
        
        except Exception as e:
        
             self.log.error("Erro ao carregar arquivo de configuracao (config.yml).")
        
             self.log.error(e)
        
             exit(1)

########################################################################
    # verifica suporte ao jira no arquivo de configuracao
    def _get_enabled_api(self):
        
        api = {}
        
        modo = '_teste'

        if  self.conf['PRODUCAO']: modo = ''


        if (self.conf['jira']['API']):
        
            self.log.info("API do JIRA habilitada no arquivo de configuracao")

            jira_url = self.conf['jira']['server' + modo]

            jira_user = self.conf['jira']['user' + modo]

            jira_password = self.conf['jira']['passw' + modo]

            self.log.info(
                "Carregando API do JIRA (url: %s, username: %s)" % (
                    jira_url, jira_user)
            )

            try:
        
                api['jira'] = jira.JIRA(
                    jira_url,
                    basic_auth=(jira_user, jira_password)
                )
        
            except Exception as e:
        
                #self.log.error("Erro ao conectar na API do Zabbix. Desabilitando.",exc_info=True)
                self.log.error("Erro ao conectar na API do JIRA. Desabilitando.")
        
                self.log.error(e)
        
                api['jira'] = False
                

        else:
        
            self.log.error("API do JIRA esta desabilitada no arquivo de configuracao.")
        
            api['jira'] = False

        # verifica suporte ao zabbix no arquivo de configuracao
        
        if (self.conf['zabbix']['API']):
        
            self.log.info("API do ZABBIX habilitada no arquivo de configuracao")


            zabbix_url = self.conf['zabbix']['server' + modo]

            zabbix_user = self.conf['zabbix']['user' + modo]

            zabbix_password = self.conf['zabbix']['passw' + modo]

            zabbix_loglevel = self.conf['zabbix']['loglevel']


            self.log.info(
                "Loading Zabbix API (url: %s, username: %s)" % (
                    zabbix_url, zabbix_user)
            )
        
            print(self.conf['zabbix'])

            try:
        
                zapi = ZabbixAPI(server=zabbix_url,
                                 log_level=zabbix_loglevel,
                                 timeout=20)
                
                zapi.login(zabbix_user,zabbix_password)
        
                api['zabbix'] = zapi
                
                
            except Exception as e:

                self.log.error("Erro ao conectar na API do Zabbix. Desabilitando.")

                self.log.error(e)

                api['zabbix'] = False

        else:

            self.log.error("Backend do Zabbix esta desativado.")

            api['zabbix'] = False

        return api
########################################################################

    def _set_alerta(self, trigger_id, ticket):

        cache_dir = self.conf['CACHE_DIR']
        
        path_abs = os.path.abspath('.')

        cache_dir = path_abs + cache_dir
        
        if not (os.path.exists(cache_dir)):

            os.makedirs(cache_dir)

        cache_file = os.path.join(cache_dir, trigger_id + '.json')

        self.log.info("Escrevendo no arquivo de cache %s" % cache_file)

        try:

            with open(cache_file, 'w') as fp:

                json.dump(ticket, fp)

                fp.close()

        except Exception as e:

            self.log.error("Erro ao escrever arquivo de cache file %s. Saindo." % cache_file)

            self.log.error(e)

            return False

        return True

########################################################################

    def _get_alerta(self, trigger_id):

        cache_dir = self.conf['CACHE_DIR']

        path_abs = os.path.abspath('.')

        cache_dir = path_abs + cache_dir

        cache_file = os.path.join(cache_dir, trigger_id + ".json")

        self.log.info("Usando arquivo de cache %s" % cache_file)

        try:

            fp = open(cache_file)

            event = json.load(fp)

            fp.close()

        except (IOError, EOFError):

            return False

        return event

########################################################################

    def _del_alerta(self, trigger_id):

        cache_dir = self.conf['CACHE_DIR']

        path_abs = os.path.abspath('.')

        cache_dir = path_abs + cache_dir

        cache_file = os.path.join(cache_dir, trigger_id + ".json")


        # remove arquivo de cache caso exista

        try:

            fp = open(cache_file)

            event = json.load(fp)

            fp.close()

            os.unlink(cache_file)

            self.log.info("Removendo arquivo de cache %s." % cache_file)

        except Exception as e:

            self.log.error("Erro ao remover arquivo de cache %s." % cache_file)

            self.log.error(e)

        return event    

########################################################################

    def run(self):

        raise NotImplementedError(

            'Voce deve implementar o seu proprio metodo run()!')
