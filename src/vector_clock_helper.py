import json

#### Estrutura queued_msgs ####
#map de tuplos {username, (msg_sender_clock, msg)}

#ao recebermos uma mensagem temos 3 opções:
#-> info que já temos descartamos a mensagem
#-> info atual adicionamos à timeline
#-> info futura (esão a faltar mensagens) adicionamos a um map
#os 3 parâmetros são maps e o username é o nome do  dono da mensagem
def check_if_valid_message(msg_vector_clock, local_vector_clock, queued_msgs, username, msg):
    if msg_vector_clock.get(username) < local_vector_clock.get(username):
        return False
    elif msg_vector_clock.get(username) == (local_vector_clock.get(username) +1):
        return True #sempre que entramos aqui de seguida temos de chamar a queued_msgs
    else:
        queued_msgs.put(username, (msg_vector_clock.get(username), msg))
        return False

#função a ser chamada sempre que introduzimos uma mensagem na timeline
#vai percorrer a lista das mensagens que estão queued daquele utilizador
def queued_msgs(local_vector_clock, queued_msgs, username, timeline):
    username_queued_msgs = queued_msgs.get(username)
    #É preciso fazer um sort. As linhas abaixo é um teste
    #data = [(1,1), (2,0)]
    #print(sorted(data, key=lambda tup: tup[1]))
    sorted(username_queued_msgs, key=lambda tup: tup[0])
    
    for queued_msg in username_queued_msgs:
        if queued_msg[0] ==  (local_vector_clock.get(username) + 1):
            timeline.append({'id': username, 'message': queued_msg[1]})