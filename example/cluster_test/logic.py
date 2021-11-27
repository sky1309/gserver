import time
from util import timer

import server
from cluster import service
from module import module


class GameModule(module.Module):

    service = None

    def on_init(self):
        server.cluster.pb_server.set_service(self.service)


gates = [1]
gamemodule = GameModule("game")
gamemodule.service = service.Service("game")


@gamemodule.service.route(1)
def login(caller, sessionid, data):
    for gate_node_id in gates:
        server.cluster.call_node(gate_node_id, "sendto_session", caller.msg_id, b'game login success', sessionid)


def loop_heartbeat():
    for gate in gates:
        server.cluster.call_node(gate, "broadcast", 0, f"heartbeat_{time.time()}".encode())


timer.add_loop_task(2, loop_heartbeat)


server.setup(gamemodule)
server.serve_forever()
