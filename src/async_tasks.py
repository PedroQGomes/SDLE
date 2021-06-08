import asyncio, json, socket
from Connection import Connection
import builder

MAX_CONN = 5
# process all messages into the Queue
@asyncio.coroutine
def task(server, loop, nickname, menu, queue):
    menu.draw()
    while True:
        msg = yield from queue.get()
        
        if not msg == '\n' and menu.run(int(msg)):
            break
        menu.draw()
    loop.call_soon_threadsafe(loop.stop)


async def task_follow(user_id, nickname, server, following, ip_address, p2p_port, user_msg):
    result = await server.get(user_id)

    if result is None:
        print('That user doesn\'t exist!')
    else:
        userInfo = json.loads(result)
        #print(userInfo)
        try:
            if userInfo['followers'][nickname]:
                print('You\'re following him!')
        except Exception:
            print('Following ' + user_id)
            following.append({'id': user_id, 'ip': userInfo['ip'], 'port': userInfo['port'],'user_msg':userInfo['user_msg']})
            userInfo['followers'][nickname] = f'{ip_address} {p2p_port}'
            asyncio.ensure_future(server.set(user_id, json.dumps(userInfo)))


# get followers port's
async def get_followers_p2p(server, nickname):
    connection_info = []
    result = await server.get(nickname)

    if result is None:
        print('ERROR - Why don\'t I belong to the DHT?')
    else:
        userInfo = json.loads(result)
        userInfo['user_msg'] += 1
        asyncio.ensure_future(server.set(nickname, json.dumps(userInfo)))
        for user, info in userInfo['followers'].items():
            connection_info.append(info)
    return connection_info


async def task_send_msg(msg, server, nickname,timeline,myMessages):
    connection_info = await get_followers_p2p(server, nickname)
    
    if len(connection_info) <= MAX_CONN:
        for follower in connection_info:
            info = follower.split()
            send_p2p_msg(info[0], int(info[1]), msg,timeline,myMessages,nickname)
    else:
        print("numero maximo de coneçoes atingida")
        redirect_alg(connection_info,msg,timeline,myMessages,nickname)

def redirect_alg(user_ids, msg,timeline,myMessages,nickname):
    users_done = MAX_CONN

   
    for follower in range(MAX_CONN):
        #print('follower nr ', follower, 'and I will redirect to:')
        if int(users_done + len(user_ids)/MAX_CONN) < len(user_ids)-1:
            sub_list = [user_ids[index] for index in range(users_done, int(users_done+ len(user_ids)/MAX_CONN))]
        else:
            sub_list = [user_ids[index] for index in range(users_done, len(user_ids))]
            
        users_done += len(sub_list)
        #print(sub_list)

        #tirar a info da simple_msg
        msg_complex = builder.complex_msg(msg, sub_list)
        info = user_ids[follower].split()
        send_p2p_msg(info[0], int(info[1]), msg_complex,timeline,myMessages,nickname)




def send_p2p_msg(ip, port, message,timeline,myMessages,nickname):
    if isOnline(ip, port):
        connection = Connection(ip, port)
        connection.connect()
        connection.send(message, timeline,myMessages,nickname)


# check if a node is online
def isOnline(userIP, userPort):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((userIP, userPort))
    if result == 0:
        print("IS ONLINE " + userIP)
        return True
    else:
        print("NOT ONLINE " + userIP)
        return False
