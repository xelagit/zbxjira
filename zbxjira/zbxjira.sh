LOG_FILE="/usr/lib/zabbix/alertscripts/zbxjira/log/zbxjira.log"
CONFIG="/usr/lib/zabbix/config.yml"


TO=$1 #Ignorar esse parametro
#echo "PARA: $1"

SUBJECT=$2 # macro {ALERT.SUBJECT} na versao 3.0 do zabbix
#echo "SUMARIO: $2"

BODY=$3 # macro {ALERT.MESSAGE} na versoa 3.0 mensagem
#echo "MENSAGEM: $3"


 msg() {
  echo "$(date + %F\ %T zbxjira.sh - INFO - ) $@" | tee -a $LOG_FILE
}


# check summary for the alert status
echo "$SUMARIO" | grep "Problema" 1> /dev/null 2>&1

if [ $? -eq 0 ]; then

  ACAO="PROBLEMA"

else

  ACAO="OK"

fi

#echo "ACAO: $ACAO"

#Recupera o id do evento na mensagem da acao no zabbix

EVENTID=$(echo "$MENSAGEM" | egrep -o  "[Ii][Dd] do [Ee]vento: [0-9]+" | egrep -o  "[0-9]+")
#echo "EVENTO: $EVENTID"

if [ -n "$EVENTID" ]; then

  msg "Enviando para o JIRA projeto Service Desk - Evento: ${EVENTID}"
  python /usr/lib/zabbix/alertscripts/zbxjira/zbxjira.py -i $EVENTID -c "$CONFIG" -o "$LOG_FILE" $ACAO "$SUBJECT" "$BODY"

else

   msg "Comando nao Executado - verificar parametros de linha de comando no script sh!"

fi
