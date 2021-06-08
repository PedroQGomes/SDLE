import socket, sys, threading, json, asyncio
import flake 
import builder
import traceback

MAX_CONN = 5
class Connection:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = True


    # bind an address
    def bind(self):
        server_address = (self.host, self.port)
        self.sock.bind(server_address)


    # create a connection
    def connect(self):
        server_address = (self.host, self.port)
        self.sock.connect(server_address)


    # put the socket in "Listen" mode
    def listen(self, timeline, server, nickname, user_msg,following,myMessages):
        self.sock.listen(1)

        #while not stop_event:
        while self.running:
            print('waiting for a connection')
            connection, client_address = self.sock.accept()
            manager = threading.Thread(target=process_request, args=(connection, client_address, timeline, server, nickname, user_msg,following,myMessages))
            manager.start()


    def stop(self):
        self.running = False
        socket.socket(socket.AF_INET, 
                  socket.SOCK_STREAM).connect((self.host, self.port))
        self.sock.close()


    # send a message to the other peer
    def send(self, msg,timeline,myMessages,nickname):
        try:
            #print("mensagem ",msg)
            self.sock.sendall(msg.encode('utf-8'))

            data = self.sock.recv(256)
            #data.decode('utf-8')
            print ('received "%s"' % data.decode('utf-8'))
            if not data.decode('utf-8') == 'ACK':
                info = json.loads(data)
                if info['type'] == 'repeat':
                    print("repeat message")
                    arr = []
                    for message in myMessages:
                        #print(message['user_msg'])
                        #print(info['lastknown'])
                        if message['user_msg'] > info['lastknown']:
                            arr.append(message)
                    str1 = builder.multiple_msg(arr,nickname)
                    #print(str1)
                    self.sock.sendall(bytes(str1, 'utf-8'))    
        finally:
            print('closing socket')
            self.sock.close()


# process the request, i.e., read the msg from socket (Thread)
def process_request(connection, client_address, timeline, server, nickname, user_msg,following,myMessages):
    try:
        print('connection from', client_address)
        while True:
            data = connection.recv(1024)
            if data:
                #data.decode('utf-8')
                print('received2 "%s"' % data.decode('utf-8'))
                result = process_message(data, timeline, server, nickname, user_msg,following,client_address,connection,myMessages)
                connection.sendall(result)
            else:
                break
    except Exception:
        traceback.print_exc()
    finally:
        connection.close()


def process_message(data, timeline, server, nickname, user_msg,following,client_address,connection,myMessages):
    info = json.loads(data)
    #print(info)
    if info['type'] == 'simple':
        #print("simple message")
        checkvalidmsg(timeline,following,info)

 
        return 'ACK'.encode('utf-8')
    elif info['type'] == 'mutiple':
        #print("multiple message")
        for m in info['arr']:
            m['timestamp'] = flake.get_datetime_from_id(m['msg_id'])
            timeline.append(m)

        for follow in following:
            if follow['id'] == info['id']:
                follow['user_msg'] = info['arr'][-1]['user_msg']

        return 'ACK'.encode('utf-8')
    elif info['type'] == 'complex':
        #print("complex message")
        connection_info = info['conn']
        #print("simpels1 ",info['msg'])
        msg = json.loads(info['msg'])
        #print("simpels2 ",msg)
        checkvalidmsg(timeline,following,msg)

        if len(connection_info) <= MAX_CONN:
            for follower in connection_info:
                user = follower.split()
                info['conn'] = []
                send_p2p_msg(user[0], int(user[1]), json.dumps(info),timeline,myMessages,nickname)
        else:
            print("Numero maximo de conexões atingida")
            redirect_alg(connection_info,info,timeline,myMessages,nickname)

        return 'ACK'.encode('utf-8')
        





def redirect_alg(user_ids, msg,timeline,myMessages,nickname):
    users_done = MAX_CONN
    #print(msg)
   
    for follower in range(MAX_CONN):
        #print('follower nr ', follower, 'and I will redirect to:')
        if int(users_done + len(user_ids)/MAX_CONN) < len(user_ids)-1:
            sub_list = [user_ids[index] for index in range(users_done, int(users_done+ len(user_ids)/MAX_CONN))]
        else:
            sub_list = [user_ids[index] for index in range(users_done, len(user_ids))]
            
        users_done += len(sub_list)
        #print(sub_list)

        #tirar a info da simple_msg
        msg_complex = builder.complex_msg(msg['msg'], sub_list)
        #print("complexa ",msg_complex)
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


def checkvalidmsg(timeline,following,info):
    for follow in following:
            
            if follow['id'] == info['id']:

                if info['user_msg'] == follow['user_msg'] + 1:
                    print("Mensagem adicionada a timeline")
                    
                    timestamp = flake.get_datetime_from_id(info['timeid'])
                    cut_timeline(timestamp,timeline)
                    follow['user_msg'] += 1
                    timeline.append({'timestamp':timestamp,'id': info['id'], 'message': info['msg'],'user_msg':info['user_msg']})
                    
                else:
                    print("Mensagem rejeitada")
                    return bytes(builder.repeat_msg(follow['user_msg'],info['user_msg']), 'utf-8')




def cut_timeline(msg, timeline):
    new_msg_timestamp = msg

    if timeline:
        data = timeline[0]['timestamp']
        while not is_valid(data, new_msg_timestamp):
            timeline.pop(0)
            if timeline:
                data = timeline[0]['timestamp']
            else : break
    

#vê se diferença entre mensagens é superior a 1 dia
def is_valid(data, new_msg_timestamp):
    difference = new_msg_timestamp - data
    seconds_in_day = 24 * 60 * 60
    diff = divmod(difference.days * seconds_in_day + difference.seconds, 60)
    #print(diff)
    if diff[1] > 10: # se passou 10 segundos
        return False
    return True
