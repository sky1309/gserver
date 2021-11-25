import threading
from typing import List
from collections import deque

from net.connmanager import Request


class MsgHandler:

    def __init__(self, max_worker=5):
        self._max_worker = max_worker
        self._thread_pool: List[ThreadHandler] = list()

        # 是否已经初始化了
        self._is_init = False
        # 路由（可能有的情况下用不到）
        self._routes = {}

    def add_to_task_queue(self, *requests: Request):
        for request in requests:
            worker_index = request.conn.id % self.get_max_worker()
            self._thread_pool[worker_index].put_requests(request)

    def get_max_worker(self) -> int:
        return self._max_worker

    def get_thread_pool(self) -> List[threading.Thread]:
        return self._thread_pool

    def stop(self):
        print("[msg handler] close threads.")
        for thread in self._thread_pool:
            thread.close()

    def start(self):
        if self._is_init:
            print("[msg handler] is staring!")
            return

        for tid in range(self._max_worker):
            t = ThreadHandler(tid, self)
            t.setDaemon(True)
            self._thread_pool.append(t)

        for t in self._thread_pool:
            t.start()

        self._is_init = True
        print(f"[msg handler] start success, count={self._max_worker}.")

    def register_route(self, name, handler):
        """路由注册"""
        if name in self._routes:
            raise NotImplementedError("duplicate route error, msg id", name)
        self._routes[name] = handler

    def handle_request(self, request):
        """默认的消息处理，可以通过继承并重写这个方法，用作其他用途"""
        handler = self._routes.get(request.msg_id)
        if not handler:
            print("not find route msg id: {}".format(request.msg_id))
            return
        handler(request)


class ThreadHandler(threading.Thread):

    def __init__(self, tid, message_handler, *args, **kwargs):
        super(ThreadHandler, self).__init__(*args, **kwargs)

        self._message_handler = message_handler

        self._requests_queue = deque()
        self._lock = threading.Lock()
        self._cond = threading.Condition()

        # 是否已经开启的状态
        self._is_open = True
        self._tid = tid

    def run(self):
        self._cond.acquire()
        while self._is_open or len(self._requests_queue) > 0:
            request, find = self.get_request()
            if not find:
                self._cond.acquire()
                self._cond.wait()
                continue

            self._message_handler.handle_request(request)

    def put_requests(self, *request: Request):
        """添加新的请求"""
        with self._lock:
            self._requests_queue.extend(request)

        if self._cond.acquire(blocking=False):
            # notify block handle thread wake up.
            self._cond.notify()
            # 释放锁
            self._cond.release()

    def get_request(self):
        """get first queue element"""
        with self._lock:
            find = True
            if len(self._requests_queue) > 0:
                request = self._requests_queue.popleft()
            else:
                request = None
                find = False
        return request, find

    def close(self):
        """关闭"""
        self._is_open = True

    def notify(self):
        """notify threading ready to exec request"""
        self._cond.notify()
