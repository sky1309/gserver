from util import timer

import server
from cluster import cluster, service

sv = service.Service("logic")
cluster.cluster.pb_server.set_service(sv)


@sv.route("foo")
def foo(name):
    print("logic foo func", name)
    for gate_node_id in cluster.cluster.gates:
        cluster.cluster.call_node(gate_node_id, "broadcast", 1, b'logic server data!!')
    return "foo"


# 定时任务
timer.add_loop_task(2, foo, "logic foo!")
server.serve_forever()
