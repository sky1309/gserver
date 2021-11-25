from twisted.internet import task
from twisted.internet import reactor

from util import atomic_counter

# 循环任务
_looping_timers = {}
# 延迟的任务
_delay_timers = {}
# 循环任务id
_timer_task_counter = atomic_counter.AtomicCounter()


def add_loop_task(interval, func, *args, now=True, **kwargs):
    """循环的任务
    参数:
      - interval: int or float 间隔时间
      - func: 执行的函数
      - now: 是否立即执行
    """
    task_id = _timer_task_counter.increment(1)
    _loop = task.LoopingCall(func, *args, **kwargs)
    _loop.start(interval, now)
    _looping_timers[task_id] = _loop
    return task_id


def stop_loop_task(task_id):
    if task_id not in _looping_timers:
        return

    _looping_timers[task_id].stop()
    del _looping_timers[task_id]


def add_later_task(interval, func, *args, **kwargs):
    """定时执行一次的任务
    """
    def wrap_func(task_id):
        # n秒后执行的任务，需要把_delay_timers中移除掉
        if task_id in _delay_timers:
            del _delay_timers[task_id]
        # 执行函数
        func(*args, **kwargs)

    taskid = _timer_task_counter.increment(1)
    _delay_timers[taskid] = reactor.callLater(interval, wrap_func, taskid)
    return taskid


def stop_later_task(task_id):
    """停止延时任务"""
    if task_id not in _delay_timers:
        return
    _delay_timers[task_id].cancel()
    del _delay_timers[task_id]
