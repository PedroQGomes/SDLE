import asyncio
import builder
import socket
import json
from P2P.Connection import Connection

class MsgSpreader:
    def __init__(self, server, username, timeline, vector_clock):
        self.server = server
        self.username = username
        self.timeline = timeline
        self.vector_clock = vector_clock

    # send message to the followers
    def send_msg(self):
        msg = input('Insert message: ')
        msg = msg.replace('\n','')
        #um nodo pode inserir informação na sua timeline
        timeline.append({'id': username, 'message': msg})
        print(msg)
        result = builder.simple_msg(msg, username)
        asyncio.ensure_future(task_send_msg(msg))

        return False
    
    async def task_send_msg(self, msg):
        connection_info = await get_user_followers(server, username, vector_clock)
        # print('CONNECTION INFO (Ip, Port)')
        for follower in connection_info:
            #print(follower)
            info = follower.split()
            send_p2p_msg(info[0], int(info[1]), msg)

    # get followers port's
    async def get_user_followers(self):
        connection_info = []
        result = await server.get(username)

        if result is None:
            print('ERROR - Why don\'t I belong to the DHT?')
        else:
            userInfo = json.loads(result)
            print(userInfo)
            userInfo['vector_clock'][username] += 1
            vector_clock[username] += 1
            asyncio.ensure_future(server.set(username, json.dumps(userInfo)))
            for user, info in userInfo['followers'].items():
                connection_info.append(info)
        return connection_info

    def send_p2p_msg(self, ip, port, message):
        if isOnline(ip, port):
            connection = Connection(ip, port)
            connection.connect()
            connection.send(message, timeline)

    # check if a node is online
    def isOnline(self, userIP, userPort):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((userIP, userPort))
        if result == 0:
            print("IS ONLINE " + userIP)
            return True
        else:
            print("NOT ONLINE " + userIP)
            return False