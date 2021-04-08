import threading
from typing import List, Dict
from collections import deque


from util.common import log
from util.exceptions import DuplicateRouteError

from iface import IRequest
from iface.imsghandler import IMsgHandler
from iface.iroute import IRoute


class MsgHandler(IMsgHandler):

    def __init__(self, max_worker=5):
        self._routes = dict()
        self._max_worker = max_worker
        self._thread_pool: List[ThreadHandler] = list()

        # 路由映射关系 map[int]IRoute
        self._routes = dict()

        # 是否已经初始化了
        self._is_init = False

    def add_to_task_queue(self, *requests: IRequest):
        for request in requests:
            worker_index = request.get_conn().get_cid() % self.get_max_worker()
            self._thread_pool[worker_index].put_requests(request)

    def add_route(self, msg_id: int, route: IRoute):
        if msg_id in self._routes:
            raise DuplicateRouteError("duplicate route error, msg id", msg_id)
        self._routes[msg_id] = route

    def get_max_worker(self) -> int:
        return self._max_worker

    def get_thread_pool(self) -> List[threading.Thread]:
        return self._thread_pool

    def stop(self):
        print("[msg handler] close threads.")
        for thread in self._thread_pool:
            thread.close()

    def start(self):
        print("[msg handler] ready start.")
        if self._is_init:
            print("[msg handler] is staring!")
            return

        for tid in range(self._max_worker):
            t = ThreadHandler(tid, self._routes)
            t.setDaemon(True)
            self._thread_pool.append(t)

        for t in self._thread_pool:
            t.start()

        self._is_init = True
        print("[msg handler] start success.")


class ThreadHandler(threading.Thread):

    def __init__(self, tid, routes: Dict[int, IRoute], *args, **kwargs):
        super(ThreadHandler, self).__init__(*args, **kwargs)

        self._requests_queue = deque()
        self._lock = threading.Lock()
        self._cond = threading.Condition()

        # 路由数据map[int]IRoute
        self._routes = routes

        # 是否已经开启的状态
        self._is_open = True
        self._tid = tid

    def run(self):
        print("[thread handler {}] running!".format(self._tid))
        self._cond.acquire()
        while self._is_open or len(self._requests_queue) > 0:
            request, find = self.get_request()
            if not find:
                self._cond.acquire()
                self._cond.wait()
                continue

            self.handle(request)

    def put_requests(self, *request: IRequest):
        """添加新的请求"""
        with self._lock:
            self._requests_queue.extend(request)

        if self._cond.acquire(blocking=False):
            # notify block handle thread wake up.
            self._cond.notify()
            # 释放锁
            self._cond.release()

    def get_request(self) -> (IRequest, bool):
        """get first queue element"""
        with self._lock:
            find = True
            if len(self._requests_queue) > 0:
                request = self._requests_queue.popleft()
            else:
                request = None
                find = False
        return request, find

    def get_condition(self) -> threading.Condition:
        return self._cond

    def handle(self, request: IRequest):
        """处理请求的逻辑"""
        route = self._routes.get(request.get_msg_id())
        if not route:
            log.warning("not find route msg id: {}".format(request.get_msg_id()))
            return

        route.do(request)

    def close(self):
        """关闭"""
        self._is_open = True
        print("[thread handler {} ] closed.".format(self._tid))

    def notify(self):
        """notify threading ready to exec request"""
        self._cond.notify()
