from util import timer

import server
from cluster import cluster, service

sv = service.Service("logic")
cluster.cluster.pb_server.set_service(sv)

gates = [1]


@sv.route(1)
def foo(caller, sessionid, data):
    print("logic foo", caller)
    for gate_node_id in gates:
        cluster.cluster.call_node(gate_node_id, "sendto_session", sessionid, 123, data)


def test_loop_task():
    for gate_node_id in gates:
        cluster.cluster.call_node(gate_node_id, "broadcast", 1, f'node{server.sys_args.nodeid} data!!'.encode())


# timer.add_loop_task(2, test_loop_task, now=False)

server.serve_forever()
