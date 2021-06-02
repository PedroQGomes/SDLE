import logging
import asyncio
import sys

from kademlia.network import Server

DEBUG = True 

# starting a node
def start_node(Port, BTPort=0): 
    print(Port ," ", "127.0.0.1" ," ", BTPort)
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

    # the first peer don't do that
    if not BTPort == 0:    
        bootstrap_node = ("127.0.0.1", int(BTPort))
        loop.run_until_complete(server.bootstrap([bootstrap_node]))
    
    return (server, loop)
