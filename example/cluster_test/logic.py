import server
from module import module


class GameModule(module.Module):

    service = None

    def on_init(self):
        server.cluster.pb_server.set_service(self.service)


gamemodule = GameModule("game", cluster=server.cluster)
gamemodule.service = module.ModuleService("game")


@gamemodule.service.route(1)
def login(caller, sessionid, data):
    server.cluster.call_node(caller.node_id, "sendto_session", caller.msg_id, b'game login success', sessionid)


@gamemodule.service.route(2)
def gate_conn_lost(caller, sessionid):
    """网关的链接断开了
    """
    print(caller, sessionid)


server.setup(gamemodule)
server.serve_forever()
