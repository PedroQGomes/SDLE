import logging
import asyncio
import sys
import socket
import traceback
from threading import Thread
from kademlia.network import Server

import tasks_helper
import builder
from LocalStorage import local_storage
from P2P.Connection import Connection

# -- Global VARS --
queue = asyncio.Queue() #cria uma rede assíncrona https://docs.python.org/3/library/asyncio-queue.html
nickname = "" #nome do user
timeline = []
following = [] #lista de p2p ports
vector_clock = {}
#!db_file = 'db'

## inicialização do nodo ####
def connect_to_bootstrap_node(server, port, p2p_port):
    loop = asyncio.get_event_loop()
    loop.set_debug(True)

    loop.run_until_complete(server.listen(port))
    print(p2p_port)
    bootstrap_node = ("127.0.0.1", p2p_port) 
    loop.run_until_complete(server.bootstrap([bootstrap_node]))
    return server, loop


def create_bootstrap_node(server, port):
    loop = asyncio.get_event_loop()
    loop.set_debug(True)

    loop.run_until_complete(server.listen(port))
    return server, loop
############################   

# Get user real ip
def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip

# put the peer in "Listen mode" for new connections
def start_p2p_listenner(server, connection):
    connection.bind()
    connection.listen(timeline, server, nickname, vector_clock)

# handler process IO request
def handle_stdin():
    data = sys.stdin.readline()
    asyncio.ensure_future(queue.put(data)) # Queue.put is a coroutine, so you can't call it directly.

# build a json with user info and put it in the DHT
async def build_user_info(server, p2p_port, ip_address):
    exists = await server.get(nickname) 
    print(nickname)                                #check if user exists in DHT
    if exists is None:
        #cria um json com a sua info para enviar para a DHT
        info = builder.user_info(nickname, p2p_port, ip_address)
        #inicia o vector clock local
        vector_clock[nickname] = 0
        #atualiza a DHT
        #print('vou adicionar esta info à DHT:\n', info)
        asyncio.ensure_future(server.set(nickname, info))
        '''
        print('adicionei esta info à DHT:\n', info)
        print('Vamos ver o que está na DHT:')
        for (key, value) in (server.storage.__iter__()):
            print('key: ', key)
            print('value: ', value)
        '''

def peer_iniciation():
    if len(sys.argv) < 3:
        sys.exit(1)

    p2p_port = sys.argv[2]

    ## kademila connection ###
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    log = logging.getLogger('kademlia')
    log.addHandler(handler)
    log.setLevel(logging.DEBUG)

    server = Server()

    #!A ligação dos nodos está a dar asneira
    if int(sys.argv[-1]) != 0:
        server, loop = connect_to_bootstrap_node(server, int(sys.argv[1]), int(sys.argv[3]))   
    else:
        server, loop = create_bootstrap_node(server, int(sys.argv[1]))

    return server, loop, p2p_port

def peer_execution(server, loop, p2p_port):
    try:
        username = input('Nickname: ')  # Get nickname from user                                                                     # Get nickname from user
        #se existir lê o json com a info do utilizador               
        (timeline, following, vector_clock) = local_storage.read_data('db'+nickname)     # TODO rm nickname (it's necessary for to allow tests in the same host

        #!Esta connection também não está a funcionar
        # acho que inicia o socket de leitura
        ip_address = get_ip_address() # !!! igual à dos mans mas acho que pode ficar assim !!! #
        print('ip_address: ', ip_address)
        connection = Connection(ip_address, int(p2p_port))
        #incia um socket listenner
        #https://docs.python.org/3/library/threading.html
        #args is the argument tuple for the target invocation. Defaults to ().
        thread = Thread(target = start_p2p_listenner, args = (server, connection, ))
        thread.start()
        loop.add_reader(sys.stdin, handle_stdin)  # Register handler to read STDIN
        asyncio.ensure_future(build_user_info(server, p2p_port, ip_address))  # Adiciona a info do utilizador à DHT e inicia o relógio a 0                                                  # Register in DHT user info
        asyncio.ensure_future(tasks_helper.get_timeline(server, nickname, following, vector_clock))     # carrega a timeline
        asyncio.ensure_future(tasks_helper.task(server, loop, queue, nickname, timeline, following, vector_clock, ip_address, p2p_port))           # Register handler to consume the queue
        loop.run_forever()                                                                  # Keeps the user online
    except Exception:
        traceback.print_exc()
        pass
    finally:
        print('Good Bye!')
        local_storage.save_data(timeline, following, vector_clock, 'db'+nickname)           # TODO rm nickname
        connection.stop()                                                                   # stop thread in "listen mode"
        server.stop()                                                                       # Stop the server with DHT Kademlia
        loop.close()                                                                        # Stop the async loop
        sys.exit(1)

######################

#recebe um port como input (para o nodo inicial devemos passar 0)
def main():
    server, loop, p2p_port = peer_iniciation()
    peer_execution(server, loop, p2p_port)

#########################

if __name__ == "__main__":
    main()
