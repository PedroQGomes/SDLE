import asyncio
import json
from P2P.Connection import Connection

class MsgSpreader:
    def __init__(self, server, username, timeline, vector_clock, following, ip_address, p2p_port):
        self.server = server
        self.username = username
        self.timeline = timeline
        self.vector_clock = vector_clock
        self.following = following
        self.ip_address = ip_address
        self.p2p_port = p2p_port

    async def task_follow(self, user_id):
        result = await server.get(user_id)

        if result is None:
            print('That user doesn\'t exist!')
        else:
            userInfo = json.loads(result)
            print(userInfo)
            try:
                if userInfo['followers'][username]:
                    print('You\'re following him!')
            except Exception:
                print('Following ' + user_id)
                following.append({'id': user_id, 'ip': userInfo['ip'], 'port': userInfo['port']})
                userInfo['followers'][nickname] = f'{ip_address} {p2p_port}'
                userInfo['vector_clock'][nickname] = 0
                asyncio.ensure_future(server.set(user_id, json.dumps(userInfo)))


    # get followers port's
    async def get_followers_p2p(self):
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
