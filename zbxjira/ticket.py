# -*- coding: utf-8 -*-
"""O Comando problema."""

from pprint import pprint
from base import Base
import sys
import logging

class Ticket(Base):
    """Cria um ticket no projeto JIRA"""

    def run(self, acao):
        
        self.api = self._get_enabled_api()
        
        self.log = logging.getLogger("zbxjira.ticket")
        
        self.log.addHandler(self.opcoes['handler'])
        
        # api jira e obrigatoria - api diz respeiro a conexao com a api
        if not (self.api['jira']):
        
            self.log.error("Ao menos a conexão com API do JIRA deve estar funcionando.")
        
            sys.exit(2)

        #id do evento da trigger do zabbix
        event_id = self.opcoes['eventid']
        
        # gerador do problema, verifica se o parametro problema esta presente
        if (acao.lower() == 'problema'):
            # cria o ticket no jira
            ticket_id = self._criar_ticket(self.api['jira'])
            # reconhece o evento da trigger no zabbix caso zabbix esteja habilitado no arquivo conf
            if (ticket_id and self.api['zabbix']):
                
                self.log.info("reconhecendo evento")
        
                self._reconhecer_alerta(event_id, ticket_id)

        # recupera o gerador do evento e fecha o ticket no jira
        elif (acao.lower() == 'ok'):
            # comentar o ticket
            self._comentar_ticket(self.api['jira'], event_id)

###################################################################

    def _procurar_id_trigger(self, event_id):

        zapi = self.api['zabbix']

        try:
         
            trigger_id = zapi.event.get({"output": ["short"],
             "eventids": [event_id],
             "selectRelatedObject":"True"})[0]['relatedObject']['triggerid']

            return trigger_id

        except Exception as e:
        
            self.log.error("Erro ao recuperar ID da trigger/alerta.")
        
            self.log.error(e)
        
            exit(1)


    def _procurar_severidade_por_evento(self,event_id):

        zapi = self.api['zabbix']
        '''
        Severity of the trigger in zabbix. 

        Possible values are: 
        0 - (default) not classified; 
        1 - information; 
        2 - warning; 
        3 - average; 
        4 - high; 
        5 - disaster.

        Severidades definidas para o JIRA
        severidade => disaster/disastre = eventos_indisponibilidade
         severidade => warning/atencao   = eventos_anormalidade
         severidade => evento_discover   = eventos_nao_monitorados
        '''
        tipo_evento = {
                '2':'eventos_anormalidade',
                '5':'eventos_indisponibilidade'
                 }
        
        trigger_id = self._procurar_id_trigger(event_id)

        

        try:
        
            severidade = zapi.trigger.get(
                {"output": ["priority"],
                "triggerids": trigger_id })

            return tipo_evento[severidade[0]['priority'][0]]

        except Exception as e:
        
            self.log.error("Erro ao recuperar Tipo de evento/severidade.")
        
            self.log.error(e)
        
            exit(1)

###########################################################
# recupera o grupo de responsabilidade do eventid informado


    def _procurar_grupo_resp_severidade(self, eventid):

        zapi = self.api['zabbix']

        grupos  = []
        
        retorno = {}
        
        retorno['severidade'] = self._procurar_severidade_por_evento(eventid)

        if retorno['severidade'] :
        
            retorno['ok'] = True
        
        else:
        
            retorno['ok'] = False


        hostid = self._procurar_host_por_evento(eventid)
        


        grupos_host = zapi.host.get({"output": ["extend"],
                                     "hostids": [hostid],
                                     "selectGroups":["groupid"]})


        #inverte a chave e o valor  {'NOME_GRUPO':9} => {9:'NOME_GRUPO'}
        gresp = { v:k  for k,v in self.conf['grupos_responsabilidade'].items()}

        try:
        
            grupos = grupos_host[0]['groups']

            for v in grupos :
            #Verifica dentre os grupos a qual o host pertence se ha um grupo 
            #de responsabilidade

                if int(v['groupid']) in gresp.keys() :
                #armazena no retorno o nome do grupo de responsabilidade 
                   retorno['grupo'] = gresp[ int(v['groupid']) ]
                   

                   return retorno
                
            self.log.info("Hostid " +hostid+ " relacionado ao evento " + eventid + " nao possui grupo de responsabilidade")

            retorno['ok'] = False

            return retorno


        except Exception as e:
        
            self.log.error("Erro ao recuperar grupo de responsabilidade.")
    
            self.log.error(e)
        
            exit(1)



#######################################################################

    def _procurar_host_por_evento(self, eventid):

        zapi = self.api['zabbix']
        
        host = zapi.event.get({"output": ["short"],
                            "eventids": [eventid],
                            "selectHosts":['triggers']})
        return host[0]['hosts'][0]['hostid']

        return retorno

################## Recupera o id o elemento de servico ###############

    def _procurar_id_elemento_servico(self, event_id):

        retorno = self._procurar_grupo_resp_severidade(event_id)

        if retorno['ok'] :
        
           sev = retorno['severidade']
        
           grp = retorno['grupo']
        
           elemento = self.conf['elemento_servico'][sev][grp]

           return elemento
           
        else:
          
          return False

########################################################################

    def _criar_ticket(self, jira_api):

        zapi = self.api['zabbix']

        event_id = self.opcoes['eventid']

        #id utilizado para armazenar no cache
        trigger_id = self._procurar_id_trigger(event_id)

        servico = ""
        
        try:
        
          self.log.info('Recuperando elemento de servico do evento %s' % event_id)
          
          servico = self._procurar_id_elemento_servico(event_id)
          
          self.log.info('Elemento recuperado %s' % servico )
          
          if not (servico):
          
             self.log.warning('Erro, id do servico invalido %s!' % servico)
        
             exit(1)
          
          
        except Exception as e:
                
                self.log.error("Erro ao recuperar elemento de serviço.")

                self.log.error(e)

                exit(1)
                
        
        ticket = {
#--------------------------------DADOS_DO_SOLICITANTE------------------------------------------
        #customfield_12110 -- reporter // reporter-field
        'reporter' : {'name':'zabbix'},                    #Solicitante
        'customfield_12103' : ['587'],                     #Departamento
        'customfield_12102' : ['159'],                     #Secretaria
        #'customfield_12600' : ['Monitoramento'],          #Cargo preenchido automaticamente
        'customfield_12213' : ['lista.monit@tjms.jus.br'], #E-mail solicitante
        'customfield_11402' : '3314-1913',                 #Telefone solicitante
#----------------------------------------------------------------------------------------------

#--------------------------------DADOS_DO_USUÁRIO----------------------------------------------
        #'customfield_15907' : {'name':'zabbix'},           #Usuário
        'customfield_12802' : ['587'],                     #Departamento
        'customfield_12803' : ['159'],                     #Secretaria
        #'customfield_12804' : ['Monitoramento'],          #Cargo preenchido automaticamente
        'customfield_12805' : ['lista.monit@tjms.jus.br'], #E-mail solicitante
        'customfield_12806' : '3314-1913',                 #Telefone usuário
#----------------------------------------------------------------------------------------------
#--------------------------------CRIAÇÃO_DO_CHAMADO--------------------------------------------
        'project' : {'id':'13100'},              #Service Desk (SD)
        'issuetype' : {'id':'31'},               #Incidente
        'summary' :  self.opcoes['resumo'],     #Resumo    
        'description' : ( self.opcoes['mensagem'] ),
        'customfield_17500' : [ str(self.conf['jira']['servico']['monitoramento']) ],              #Monitoramento
        'customfield_17501' : [ str(self.conf['jira']['categoria']['Evento_de_Alerta']) ],         #Evento de Alerta
        'customfield_17502' : [ str(servico) ]        #Elemento do Servico
        }

       # criar um ticket
        try:
            
            ticket_id = jira_api.create_issue(ticket)
            
        
        except Exception as e:
            
            self.log.error("Erro ao criar ticket.")
            
            self.log.error(e)
            
            sys.exit(1)

        #self.log.info("Ticket criado %s" % ticket_id)

        self.log.info("Evento do Zabbix detectado. Tentando escrever ticket no cache.")

        self.log.info('ID da trigger do evento %s' % trigger_id)

        self._set_alerta(
                trigger_id,
                ticket_id.key
            )

        return ticket_id.key
        
########################################################################

    def _comentar_ticket(self, jira_api, event_id=False):
        
        trigger_id = self._procurar_id_trigger(event_id)

        if (trigger_id):

            self.log.info("Zabbix event ID detectado. Lendo do cache.")

            
            #recupera  do cache pelo id da trigger que lancou o evento           
            ticket_id = self._get_alerta(trigger_id)
            
            if (ticket_id):
            
                ticket = self._procurar_ticket_por_id(jira_api, ticket_id)
            
            else:
            
                self.log.error("Nao pode encontrar o ticket no cache.")
                
                sys.exit(1)
            

        if (ticket):
            
            self.log.info("id do ticket encontrado: %s" % ticket.key)
            # close issue
            #close_transition = self.conf['jira']['JIRA_APLICAR_SOLUCAO']
            
            '''
            Transitions sao as opcoes/acoes definidas no jira de acordo com a
            situacao do nosso ticket/issue. Em nosso ambiente e na situacao 
            "em atendimento" algumas Transitions sao: editar,Escalar N2,
            recategorizar, cancelar, aplicar solucao, etc ...
            A transitions que utilizariamos esta definida no zbxjira.yml,
            "Aplicar solucao ou Cancelar". No contexto que trabalhamos
            o Zabbix jamais irá fechar ou iniciar um ticket, apenas cria-lo,
            mesmo porque apenas o usuário responsável pode fecha-lo/soluciona-lo.
            Apos o encerramento do alerta o script adicionara um 
            comentario ao ticket levando em conta uma possivel solucao feita pela
            equipe responsavel.
            ''' 
            
            try:
                comentario = jira_api.add_comment(ticket.key, self.opcoes['mensagem']) 
                self.log.info('Comentario de retorno id %s adicionado' %comentario)
                
                #comment.update(body = 'updated comment body')
                #comment.delete()
                #jira_api.transition_issue(
                #    ticket.key,
                #    close_transition,
                #    resolution=self.opcoes['descricao'],
                #   comment=self.opcoes['descricao'] #mensagem da resolucao
                #)
                
                #apaga a referencia da trigger/alerta do arquivo de cache
                self._del_alerta(trigger_id)
                
            except Exception as e:
                
                self.log.error("Erro ao comentar ticket %s" % ticket.key)
                
                self.log.error(e)
                
                sys.exit(1)

        else:
            
            self.log.error("Nao encontrou o id do ticket. Nao e possivel comenta-lo.")


########################################################################

    def _procurar_ticket_por_id(self, jira_api, ticket_id):

        try:

            ticket = jira_api.issue(ticket_id)

        except Exception as e:

            self.log.error("Nao pode consultar ticket/SD pelo chave/id %s" % ticket_id)

            self.log.error(e)

            return False

        if ticket:

            return ticket

        else:

            return False

########################################################################

    def _reconhecer_alerta(self, event_id, ticket_id):

        zapi = self.api['zabbix']

        jira_url = self.conf['jira']['server_teste']

        ticket_url = jira_url + "/browse/%s" % ticket_id

        try:
            zapi.event.acknowledge({
                'eventids':event_id,
                'message':"Evento da trigger reconhecido pelo JIRA: \n%s" % ticket_url
            })
        except Exception as e:

            self.log.error("Erro enquanto reconhecendo Alerta Zabbix %s" % event_id)

            self.log.error(e)

            return False

        return True

