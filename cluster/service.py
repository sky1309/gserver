import enum
import threading

from twisted.internet import threads
from twisted.python import log


class DuplicateRegisterError(Exception):
    """路由的重复注册"""
    pass


class EServiceMode(enum.IntEnum):
    """服务的工作方式"""
    # 同步
    SYNC = 0
    # 异步
    ASYNC = 1


class Service:
    # 工作方式
    mode = EServiceMode.SYNC

    def __init__(self, name):
        self.name = name
        # 路由key是字符串，value是一个callable的
        self._handlers = {}
        # 可重入锁，同一个线程中可以重复获取
        self._lock = threading.RLock()

    def __str__(self):
        return f"Service_{self.name}:"

    def route(self, name):
        def wrap(func):
            self.register_handler(name, func)
        return wrap

    def register_handler(self, name, handler):
        # 注册路由
        if name in self._handlers:
            raise DuplicateRegisterError(f"{self} duplicate register handler: {name}!")
        self._handlers[name] = handler

    def delete_handler(self, name):
        """移除路由"""
        if name not in self._handlers:
            log.err(f"{self} unregistered handler: {name}!")
            return

        del self._handlers[name]

    ###########
    # 调用
    ###########
    def call_handler(self, name, *args, **kwargs):
        if self.mode == EServiceMode.ASYNC:
            # 异步
            return self._handle_async(name, *args, **kwargs)
        else:
            # 同步
            return self._handle_sync(name, *args, **kwargs)

    def _handle_sync(self, name, *args, **kwargs):
        if name not in self._handlers:
            log.err(f"{self} unregistered handler: {name}!")
            return

        with self._lock:
            result = self._handlers[name](*args, **kwargs)

        return result

    def _handle_async(self, name, *args, **kwargs):
        if name not in self._handlers:
            log.err(f"{self} unregistered handler: {name}!")
            return

        return threads.deferToThread(self._handlers[name], *args, **kwargs)
