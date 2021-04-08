from typing import Dict

from iface import IServer, IConnectionOperator, ISocketConnection


class ConnectionOperator(IConnectionOperator):

    def __init__(self, server: IServer):
        self._server = server

    def get_conns(self) -> Dict[int, ISocketConnection]:
        return self._server.get_conns()

    def start(self):
        """开启，这里面可以增加一些多线程的任务，广播推送什么的"""
        print("conn operator started!")
