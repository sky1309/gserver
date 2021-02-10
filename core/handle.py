import threading
import collections


class RequestHandleThread(threading.Thread):
    """虽然这是单独的一个线程，但是如果一直while true会导致资源的浪费，
    还是需要通过锁来把自己进入睡眠的装备，避免资源的浪费。
    """
    def __init__(self, *args, **kwargs):
        super(RequestHandleThread, self).__init__(*args, **kwargs)

        # 等待锁和读数据锁
        self.wait_lock = threading.Lock()
        self.read_write_lock = threading.Lock()

        self.queue = collections.deque()

    def get(self):
        with self.read_write_lock:
            if not self.queue:
                with self.wait_lock:
                    # 先释放掉读写锁，可以让别人能够put数据
                    self.read_write_lock.release()
                    # 让自己进入死锁，等待别人来解锁(self.put)
                    self.wait_lock.acquire()
                    # 如果有线程吧数据送入到了self.queue中去后，由于当前在with内，并且当前的读写锁是被释放掉的，
                    # 所以这里需要重新获取一次，用于with.__exist__后使用
                    self.read_write_lock.acquire()
            data = self.queue.popleft()
        return data

    def put(self, data):
        with self.read_write_lock:
            # 拿到等待锁，如果有等待中，那么
            self.queue.append(data)

            # 不管自己时候拿到了lock，都直接release
            if self.wait_lock.locked():
                self.wait_lock.release()

    def run(self):
        while True:
            handler, request = self.get()
            handler(request)
