from log import log

from module import module as pmodule


# 所有注册的模块
_modules = {}


def setup(module: pmodule.Module) -> bool:
    # 注册模块
    if module.name in _modules:
        log.lgserver.warning(f"module <{module.name}> duplicate setup！")
        return False

    _modules[module.name] = module


def init():
    # 初始化所有的模块
    for module in _modules.values():
        module.on_init()


def start():
    # 启动所有的模块
    for module in _modules.values():
        module.start()


def stop():
    # 停止所有的模块
    for module in _modules.values():
        module.stop()
