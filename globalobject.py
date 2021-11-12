# 全局的前端连接factory
netfactory = None


def netservice_handler(name):
    """注册基础网络的路由
    eg:
      @register_net_factory_handler(1)
      def foo(a, b):
        pass
    """
    def process(func):
        netfactory.msg_handler.register_route(name, func)
    return process
