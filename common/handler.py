from common import log


def process_route_fn(handler, fn, name=None):
    if name is None:
        name = fn.__name__

    handler.route(name, fn)
    return fn


class BaseHandler:

    def __init__(self):
        # 所有的路由，key，value的形式
        self._routes = {}

    def route(self, name, fn):
        """注册路由"""
        assert name not in self._routes, f"重复注册路由: {name}."
        log.lgserver.debug(f"注册路由: {name}")
        self._routes[name] = fn

    def _process_route_fn(self, fn, name=None):
        if name is None:
            name = fn.__name__

        self.route(name, fn)
        return fn

    def route_method(self, fn=None, *, name=None):
        # 注册路由的装饰器
        # 1.通过 @handler.route_method的形式注册的
        # 2.通过 @handler.route_method(name="xxx") 的形式注册的
        def wrap(func):
            return self._process_route_fn(func, name)

        if fn is None:
            return wrap

        return wrap(fn)

    def dispatch(self, key, *args, **kwargs):
        if key not in self._routes:
            log.lgserver.warning(f"没有注册的路由: {key}")
            return

        return self._routes[key](*args, **kwargs)


class MsgHandler(BaseHandler):
    def process_package(self, package):
        """处理消息包"""
        raise NotImplementedError()
