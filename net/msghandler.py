import json

from common import handler, log


class JsonMsgHandler(handler.MsgHandler):
    # json 消息处理
    def process_package(self, package):
        """默认的数据结构
        {
            "a": "路由名字",
            // 参数
            "d": {},
            // 客户端回调id
            "h": 1
        }
        """
        log.lgserver.debug(f"=== Receive: {package}")
        parsed_data = json.loads(package.data.decode())
        self.dispatch(parsed_data["a"], package.conn, parsed_data)


class PBMsgHandler(handler.MsgHandler):
    # protocol buffer
    def process_package(self, package):
        pass
