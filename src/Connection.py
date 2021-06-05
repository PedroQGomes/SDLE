import socket, sys, threading, json, asyncio
import flake 
import builder
import traceback
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
    def send(self, msg,timeline,myMessages):
        try:
            self.sock.sendall(msg.encode('utf-8'))

            data = self.sock.recv(256)
            print ('received1 "%s"' % data.decode('utf-8'))
            if not data.decode('utf-8') == 'ACK':
                info = json.loads(data)
                if info['type'] == 'repeat':
                    print("repeat message")
                    arr = []
                    for message in myMessages:
                        print(message['user_msg'])
                        print(info['lastknown'])
                        if message['user_msg'] > info['lastknown']:
                            arr.append(message)
                    str1 = builder.multiple_msg(arr)
                    print(str1)
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
    print(info)
    if info['type'] == 'simple':
        print("simple message")
        for follow in following:
            
            if follow['id'] == info['id']:

                if info['user_msg'] == follow['user_msg'] + 1:
                    print("boa msg")
                    timestamp = flake.get_datetime_from_id(info['timeid'])
                    timeline.append({'timestamp':timestamp,'id': info['id'], 'message': info['msg'],'user_msg':info['user_msg']})
                    
                else:
                    print("msg fora de hora")
                    return bytes(builder.repeat_msg(follow['user_msg'],info['user_msg']), 'utf-8')

 
        return 'ACK'.encode('utf-8')
    elif info['type'] == 'mutiple':
        print("multiple message")
        for m in info['arr']:
            m['timestamp'] = flake.get_datetime_from_id(m['msg_id'])
            timeline.append(m)
        return 'ACK'.encode('utf-8')
            


        

    



def get_messages(id, timeline, n):
    list = []
    for m in timeline:
        if m['id'] == id:
            list.append(m)
    print(list)
    print(list[-n:])
    return list[-n:]


def record_messages(data, timeline):
    info = json.loads(data)
    list = json.loads(info['list'])
    for m in list:
        timeline.append({'id': m['id'], 'message': m['message']})
