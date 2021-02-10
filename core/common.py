import enum
import logging


logging.basicConfig(level=logging.INFO)
log = logging.getLogger()


class ResponseStatusEnum(enum.IntEnum):
    ok = 0
    unimplemented = 1
    unpack_error = 2
