from core import server

s = server.Server(("127.0.0.1", 8000), 5)


@s.route("hello_world")
def hello_world(request):
    request.client.send({
        "c": "hello world."
    })


if __name__ == '__main__':
    s.serve_forever()
