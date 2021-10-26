import server

from net import msghandler
from net.connmanager import Request, Response


def ping_view(request: Request):
    request.conn.send_response(Response(2, b'response body'))


msghandler.register_route(1, ping_view)

server.set_connection_lost(lambda d: print("offline callback."))


if __name__ == '__main__':
    server.serve_forever(8000)
