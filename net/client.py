from iface import IClient, ISocketConnection


class Client(IClient):

    def __init__(self, cid: int, conn: ISocketConnection):
        """初始化
        """
        self._cid: int = cid

        self._conn = conn

        self._is_close = False

    def get_cid(self) -> int:
        return self._cid

    def set_cid(self, cid: int):
        self._cid = cid
