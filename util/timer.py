from twisted.internet import task
from twisted.internet import reactor

from util import atomic_counter

# 循环任务
_looping_timers = {}
# 循环任务id
_looping_timer_counter = atomic_counter.AtomicCounter()


def add_loop_task(interval, func, *args, now=True, **kwargs):
    """循环的任务
    参数:
      - interval: int or float 间隔时间
      - func: 执行的函数
      - now: 是否立即执行
    """
    _loop_id = _looping_timer_counter.increment(1)
    _loop = task.LoopingCall(func, *args, **kwargs)
    _loop.start(interval, now)
    _looping_timers[_loop_id] = _loop
    return _loop_id, _loop


def stop_loop_task(loop_id):
    if loop_id not in _looping_timers:
        return

    _looping_timers[loop_id].stop()
    del _looping_timers[loop_id]


def add_later_task(interval, func, *args, **kwargs):
    """定时执行一次的任务
    """
    reactor.callLater(interval, func, *args, **kwargs)
