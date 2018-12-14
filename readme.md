# zbxjira

Cria Tickets no JIRA dentro projeto SD(Service Desk) de acordo com eventos de trigger do Zabbix
reconhecendo-os no Zabbix e comentando-os no JIRA caso o alerta da trigger seja reparado  

Esta solução foi baseado dos scripts do repositório https://github.com/Movile/zabbix2jira
e adaptado para nossa ambiente.

## Pre-requisitos

pip install -r meus_requirements.txt

## Configurando o script para rodar.

Caminhos padrões:

- Arquivo de configuração: /usr/lib/zabbix/config.yml
   (O arquivo de configuração é utilizado por outros
   scripts. Por tal motivo recomendamos não alterar o seu caminho)
    
- Log: /usr/lib/zabbix/alertscripts/zbxjira/log/zbxjira.log
- Cache Directory: /usr/lib/zabbix/alertscripts/zbxjira/cache
  

Copie o arquivo de configuração para o caminho indicado acima.
e altere usuários, senha e links de endereço caso seja necessário.

## Integrando com o Zabbix 

Crie uma mídia de usuário e nos campos abaixo insira:
*  Nome: zabbix-jira
*  Tipo: Script
*  Nome: zbxjira/zbxjira.sh

Crie uma ação e nos campos abaixo insira:
*  Nome: Defina um nome
*  Tipo: Script

Nos campos seguintes insira o conteúdo exatamente como segue:
*  Assunto padrão: 
		Problema - ID Alerta {TRIGGER.ID}: {TRIGGER.NAME}
*  Mensagem padrão: 
		ID do evento: {EVENT.ID}

		Verificar procedencia do alerta:
		"{TRIGGER.NAME}"
		host: {HOST.HOST}
		IP: {HOST.IP}
		Data/Hora: {EVENT.DATE} | {EVENT.TIME}

*  Mensagem de recuperação:Selecione
*  Assunto de recuperação: 
		OK - ID de Alerta {TRIGGER.ID}: {TRIGGER.NAME}
*  Mensagem de recuperação:
		ID do evento: {EVENT.ID}

		O evento de alerta/trigger :
		"{TRIGGER.NAME}"
		foi encerrado. O ticket relacionado pode ter sido resolvido pela equipe responsavel. 

		Duração do Problema: {EVENT.AGE}
		host: {HOST.HOST}
		IP: {HOST.IP}
		Data/Hora de retorno: {EVENT.RECOVERY.DATE} | {EVENT.RECOVERY.TIME}

		Comentario adicionando automaticamento pelo Zabbix.

*  Ativo: selecione

Adicione as seguintes condições ou personalize-as de acordo com 
sua necessidade:

* A Status de manutenção não em manutenção
* B Valor da Trigger = PROBLEMA
* C Severidade da Trigger = (Desastre ou Atenção ....)
* ou outras condições.....

Na aba "Ações" em "Enviar para usuários", por padrão, escolha o usuário "zabbixapi".
Obs: É indiferente o usuário, apenas tenha certeza que o usuário possua em seus cadastro 
de mídia de usuário a mídia "zabbix-jira".

Exemplos de teste na linha de comando
------------------------------------
Para utilizar os scripts em modo de teste altere no config.yml
a chave PRODUCAO: False e confirme se os endereços dos servidores
testes conferem.

	O script Shell efetua parses do assunto e da mensagem para extrair a
	ação a ser tomada e o ID do evento, por esse motivo os parametros SUBJECT 
	e BODY devem seguir formato do exemplo abaixo. Utilize um ID de evento válido.

Sintaxe dos parametros de linha de comando
com o shell script:

	zbxjira.sh <to> <subject> <body> 
	zbxjira.sh "" "Problema - Nome da Trigger" "ID do evento: 1234564879"
	zbxjira.sh "" "OK - Nome da Trigger" "ID do evento: 123456789" 
  

Sintaxe dos parametros de linha de comando
com o python script:

	zbxjira.py -i <EVENTO_ID> -c <CONFIG> -o <LOG> <ACAO[PROBLEMA|OK]> <RESUMO> <MENSAGEM> 
	zbxjira.py -i  123456789 -c "/caminho/config.yml/"  -o "zbxjira/log/zbxjira.log" PROBLEMA "Alerta tal" "Verificar Alerta" 
	zbxjira.py -i  123456789 -c "/caminho/config.yml/"  -o "zbxjira/log/zbxjira.log" OK "Evento de Alerta tal" "Verificar Alerta" 





