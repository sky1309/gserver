from net import server
from net.msghandler import MsgHandler


if __name__ == '__main__':
    s = server.Server(("127.0.0.1", 8000), 5, MsgHandler())
    s.serve_forever()
