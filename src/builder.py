import json

def user_info(nickname, ip_address, p2p_port):
    info = {'ip': ip_address, 'port': p2p_port, 'followers': {}, 'user_msg': 0}
    return json.dumps(info)


def simple_msg(msg, nickname,msg_id,user_msg):
    simple_msg = {'type': 'simple', 'msg': msg, 'id': nickname,'timeid':msg_id,'user_msg':user_msg}
    return json.dumps(simple_msg)


def timeline_msg(id, vclock, n):
    msg = {'type': 'timeline', 'id': id, 'v_clock': vclock, 'n': n}
    return json.dumps(msg) 