from util import timer

import server
from cluster import service

sv = service.Service("logic")
server.cluster.pb_server.set_service(sv)

gates = [1]


@sv.route(1)
def test(caller, sessionid, data):
    for gate_node_id in gates:
        server.cluster.call_node(gate_node_id, "sendto_session", caller.msg_id, b'logic test data.', sessionid)


def test_loop_task():
    for gate_node_id in gates:
        server.cluster.call_node(gate_node_id, "broadcast", 1, f'node{server.sys_args.nodeid} data!!'.encode())


timer.add_loop_task(2, test_loop_task, now=False)

server.serve_forever()
