from net import server


if __name__ == '__main__':
    s = server.Server(("127.0.0.1", 8000), 5)
    s.serve_forever()
