import asyncio, json, socket
import builder
from P2P.Connection import Connection

def menu(server, loop, queue, nickname, timeline, following, vector_clock, ip_address, p2p_port):
    print('1 - Show timeline')
    print('2 - Follow username')
    print('3 - Send message')
    print('0 - Exit')

    option = int(input("\n"))

    '''
     #Alterar isto
        msg = yield from queue.get() #! não faço ideia que if é este
        print('msg --> ', msg)
        if not msg == '\n':
            break
    '''
    if option == 1:
        show_timeline(timeline)
    elif option == 2:
        follow_user(server, nickname, following, ip_address, p2p_port, vector_clock)
    elif option == 3:
        send_msg(server, nickname, vector_clock, timeline)
    else:
        exit_loop()


# process all messages into the Queue
@asyncio.coroutine
def task(server, loop, queue, nickname, timeline, following, vector_clock, ip_address, p2p_port):
    menu(server, loop, queue, nickname, timeline, following, vector_clock, ip_address, p2p_port)
    while True:
        menu(server, loop, queue, nickname, timeline, following, vector_clock, ip_address, p2p_port)
    loop.call_soon_threadsafe(loop.stop)


####################
# show own timeline
def show_timeline(timeline):
    print('\n\n\n')
    print('_______________ Timeline _______________')
    for m in timeline:
        print(m['id'] + ' - ' + m['message'])
    print('________________________________________')
    print('\n\n\n')
    return False

# get timeline to the followings TODO
async def get_timeline(server, nickname, following, vector_clock):
    for user in following:
        result = await server.get(user['id'])
        result2 = await server.get(nickname)
        if result is not None and result2 is not None:
            userInfo = json.loads(result)
            ownInfo = json.loads(result2)
            random_follower, n = await get_random_updated_follower(user, userInfo, ownInfo, nickname, vector_clock)
            if random_follower is not None:
                ask_for_timeline(random_follower[0], random_follower[1], user['id'], n)

 # temos de implementar o XOR
async def get_random_updated_follower(user, userInfo, ownInfo, nickname, vector_clock):
    print("RANDOM FOLLOWER")
    id = user['id']
    user_followers = userInfo['followers']
    while(user_followers):
        random_follower = random.choice(list(user_followers.keys()))
        random_follower_con = userInfo['followers'][random_follower]
        info = random_follower_con.split()
        print(userInfo['vector_clock'])
        print(vector_clock)
        if userInfo['vector_clock'][id] > vector_clock[id] and random_follower != nickname and isOnline(info[0], int(info[1])):
        #if random_follower != nickname and async_tasks.isOnline(info[0], int(info[1])):
            print("FOUND")
            return info, int(userInfo['vector_clock'][id]) - vector_clock[id] 
        user_followers.pop(random_follower)
    print("FAILED")
    if userInfo['vector_clock'][id] > vector_clock[id]:
        return [user['ip'], user['port']], int(userInfo['vector_clock'][id]) - vector_clock[id] 
    else:
        return None, 0


# send a message to a node asking for a specific timeline
def ask_for_timeline(userIp, userPort, TLUser, n, vector_clock, timeline):
    msg = builder.timeline_msg(TLUser, vector_clock, n)
    send_p2p_msg(userIp, int(userPort), msg, timeline)
    print('ASKING FOR TIMELINE')

########################## Follow user #######################################

# follow a user. After, he can be found in the list "following"
def follow_user(server, nickname, following, ip_address, p2p_port, vector_clock):
    user = input('User Nickname: ')
    #user_id = user.replace('\n', '')
    print(server)
    #método que vai à DHT ver se o utilizador existe e trata de fazer as operações necessárias
    asyncio.ensure_future(task_follow(user, nickname, server, following, ip_address, p2p_port, vector_clock))
    return False


#função chamada quando tentamos seguir um novo utilizador
async def task_follow(user_id, nickname, server, following, ip_address, p2p_port, vector_clock):
    print('##')
    result = await server.get(user_id) #o nodo vai à DHT ver se o user_id existe
    print('##')
    if result is None:
        print('That user doesn\'t exist!')
    else:
        userInfo = json.loads(result)
        print(userInfo)
        try:
            if userInfo['followers'][nickname]:
                print('You\'re following him!')
        except Exception:
            print('Following ' + user_id) #passamos a seguir o utilizador e atulizamos a info do nodo
            following.append({'id': user_id, 'ip': userInfo['ip'], 'port': userInfo['port']})
            userInfo['followers'][nickname] = f'{ip_address} {p2p_port}'
            userInfo['vector_clock'][nickname] = 0
            asyncio.ensure_future(server.set(user_id, json.dumps(userInfo))) #atualizamos a DHT

########################### Send message ######################################

def send_msg(server, nickname, vector_clock, timeline):
    msg = input('Insert message: ')
    msg = msg.replace('\n','')
    timeline.append({'id': nickname, 'message': msg})
    print(msg)
    result = builder.simple_msg(msg, nickname) #builds json message
    #manda mensagens para cada nodo que segue, atualiza o vetor clock e a DHT
    asyncio.ensure_future(task_send_msg(result, server, nickname, vector_clock))

    return False

async def task_send_msg(msg, server, nickname, vector_clock):
    #vai buscar uma lista com toda info que tem dos nodos que segue
    connection_info = await get_followers_p2p(server, nickname, vector_clock)
    # print('CONNECTION INFO (Ip, Port)')
    for follower in connection_info:
        #print(follower)
        info = follower.split()
        #manda mensagem para cada utilizador
        send_p2p_msg(info[0], int(info[1]), msg)

#establece uma conexão  e envia uma mensagem
def send_p2p_msg(ip, port, message, timeline=None):
    if isOnline(ip, port):
        connection = Connection(ip, port)
        connection.connect()
        connection.send(message, timeline)

# get followers port's (chamada por task_send_msg)
async def get_followers_p2p(server, nickname, vector_clock):
    connection_info = []
    result = await server.get(nickname)

    if result is None:
        print('ERROR - Why don\'t I belong to the DHT?')
    else:
        userInfo = json.loads(result)
        print(userInfo)
        #atualizamos o vector clock interno e na mensagem e no próprio nodo
        userInfo['vector_clock'][nickname] += 1
        vector_clock[nickname] += 1
        #atualiza a DHT com o novo vector clock
        asyncio.ensure_future(server.set(nickname, json.dumps(userInfo)))
        #guarda a info que tem de cada nodo que segue
        for user, info in userInfo['followers'].items():
            connection_info.append(info)
    return connection_info

# check if a node is online (chamada pela get_random_updated_follower, que por sua vez é chamada pela get_timeline)
def isOnline(userIP, userPort):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((userIP, userPort))
    if result == 0:
        print("IS ONLINE " + userIP)
        return True
    else:
        print("NOT ONLINE " + userIP)
        return False

############### Exit ###################
def exit_loop():
    return True