from util import timer

import server
from cluster import cluster, service

sv = service.Service("logic")
cluster.cluster.pb_server.set_service(sv)


@sv.route(1)
def foo(nodeid, sessionid, data):
    print("foo", nodeid, sessionid, data)
    for gate_node_id in cluster.cluster.gates:
        cluster.cluster.call_node(gate_node_id, "broadcast", 1, b'logic foo!!')
        timer.add_later_task(3, cluster.cluster.call_node, gate_node_id, "sendto_session", sessionid, 123, b'ss')

    return "foo"


def test_loop_task():
    for gate_node_id in cluster.cluster.gates:
        print(f'test_loop_task, nodeid={gate_node_id}')
        cluster.cluster.call_node(gate_node_id, "broadcast", 1, b'logic server data!!')


timer.add_loop_task(3, test_loop_task, now=False)

server.serve_forever()
