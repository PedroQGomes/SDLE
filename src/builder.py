import json

def user_info(nickname, ip_address, p2p_port):
    info = {'ip': ip_address, 'port': p2p_port, 'followers': {}, 'vector_clock': {nickname: 0}}
    return json.dumps(info)

#vai precisar de passar o vector clock para depois compararmos entre mensagens
#vai receber também uma lsita de seguidores que ainda não receberam a mensagem
#quando um nodo recebe esta mensagem vê a lista dos nodos que ainda não receberam a msg
#e envia a uma percentagem deles
#quando a lista estiver fazia todos os nodos receberam
def simple_msg(msg, nickname):
    simple_msg = {'type': 'simple', 'msg': msg, 'id': nickname}
    return json.dumps(simple_msg)


def timeline_msg(id, vclock, n):
    msg = {'type': 'timeline', 'id': id, 'v_clock': vclock, 'n': n}
    return json.dumps(msg) 