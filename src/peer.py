from asyncio.futures import Future
from asyncio.tasks import sleep
import logging, asyncio, sys, socket, json, threading, random
from threading import Thread
import traceback
from Connection import Connection
from Menu.Menu import Menu
import Menu.Menu as menu
from Menu.Item import Item
import async_tasks
import builder
from kademlia.network import Server
import flake 
from datetime import datetime


try:
    from asyncio import ensure_future
except ImportError:
    print("boasdnasd")


queue = asyncio.Queue()
p2p_port = ""
nickname = ""
ip_address = ""
timeline = []
myMessages = []
following = []
user_msg = 0
DEBUG = False 




def handle_stdin():
    data = sys.stdin.readline()
    asyncio.ensure_future(queue.put(data)) # Queue.put is a coroutine, so you can't call it directly.



def build_menu():
    menu = Menu('Menu')
    menu.add_item(Item('1 - Show timeline', show_timeline))
    menu.add_item(Item('2 - Follow username', follow_user))
    menu.add_item(Item('3 - Send message', send_msg))
    menu.add_item(Item('4 - Show folowing', get_folowing))
    menu.add_item(Item('0 - Exit', exit_loop))
    return menu

def get_folowing():
    print(following)
    return False


def get_nickname():
    nick = input('Nickname: ')
    return nick.replace('\n', '')



def follow_user():
    user = input('User Nickname: ')
    user_id = user.replace('\n', '')
    print(server)
    asyncio.ensure_future(async_tasks.task_follow(user_id, nickname, server, following, ip_address, p2p_port, user_msg))
    return False


# show own timeline
def show_timeline():
    menu.clear()

    print('_______________ Timeline _______________')
    for m in timeline:
        data = datetime.strftime(m['timestamp'],'%Y-%m-%d %H:%M:%S')
        print(data + ' - ' + m['id'] + ' - ' + m['message'] + ' - ' + str(m['user_msg']))
    print('________________________________________')
    input('Press Enter')
    menu.clear()
    return False


def send_msg():
    msg_id = flake.generator(12).__next__()

    time = flake.get_datetime_from_id(msg_id)
    #print(msg_id)
    #print(time)
    msg = input('Insert message: ')
    msg = msg.replace('\n','')

    global user_msg 
    user_msg += 1
    timeline.append({'timestamp':time,'id': nickname, 'message': msg,'user_msg':user_msg})
    myMessages.append({'msg_id':msg_id,'id': nickname, 'message': msg,'user_msg':user_msg})
    #print(msg)
    result = builder.simple_msg(msg, nickname,msg_id,user_msg)
    print(result)
    asyncio.ensure_future(async_tasks.task_send_msg(result, server, nickname,timeline,myMessages))

    return False


# exit app
def exit_loop():
    return True



def check_argv():
    if len(sys.argv) < 3:
        print("Usage: python peer.py <port_dht> <port_p2p> <bootstrap port>")
        sys.exit(1)


def ask_for_timeline(userIp, userPort, TLUser, n):
    msg = builder.timeline_msg(TLUser, vector_clock, n)
    async_tasks.send_p2p_msg(userIp, int(userPort), msg, timeline)
    print('ASKING FOR TIMELINE')



async def build_user_info():
    user = await server.get(nickname)                                #check if user exists in DHT
    if user is None:
        info = builder.user_info(nickname, ip_address, p2p_port)
        asyncio.ensure_future(server.set(nickname, info))



def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


def bind_p2p_listenner(connection):
    connection.bind()
    connection.listen(timeline, server, nickname, user_msg,following,myMessages)

def start_p2p_listenner(ip_address,p2p_port):
    connection = Connection(ip_address, int(p2p_port))
    thread = Thread(target = bind_p2p_listenner, args = (connection, ))
    thread.start()
    return connection


def init_node(Port, BTPort): 
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    # DEBUG
    if DEBUG:
        log = logging.getLogger('kademlia')
        log.addHandler(handler)
        log.setLevel(logging.DEBUG)

    server = Server()


    loop = asyncio.get_event_loop()
    loop.run_until_complete(server.listen(Port))


    if DEBUG:
        loop.set_debug(True)

    if not BTPort == 0:    
        bootstrap_node = ("127.0.0.1", int(BTPort))
        loop.run_until_complete(server.bootstrap([bootstrap_node]))
    
    return (server, loop)





check_argv()
p2p_port = sys.argv[2]
ip_address = get_ip_address()                                                           # Get ip address from user
(server, loop) = init_node(int(sys.argv[1]),int(sys.argv[3]))
try:
    connection = start_p2p_listenner(ip_address,p2p_port)

    print('Peer is running...')
    nickname = get_nickname()                                                           # Get nickname from user
    user_msg = 0                         
    

    loop.add_reader(sys.stdin, handle_stdin)                                            # Register handler to read STDIN
    asyncio.ensure_future(build_user_info())                                                    # Register in DHT user info

    m = build_menu()
    asyncio.ensure_future(async_tasks.task(server, loop, nickname, m, queue))                   # Register handler to consume the queue
    loop.run_forever()                                                                  # Keeps the user online
except Exception:
    traceback.print_exc()
    pass
finally:
    print('Shuting down server!')
    connection.stop()                                                                   # stop thread in "listen mode"
    server.stop()                                                                       # Stop the server with DHT Kademlia
    loop.close()                                                                        # Stop the async loop
    sys.exit(1)                                                      
