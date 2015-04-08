import datetime
from functools import partial

import tornado.ioloop
from tornado import gen
from tornado.concurrent import Future

from eibconnection import EIBConnection, EIBBuffer
from eibd_stack import LPDUFrame, LPDUDataFrame

addr_types = {
    LPDUDataFrame.GROUP_ADDRESS: 'group address',
    LPDUDataFrame.INDIVIDUAL_ADDRESS: 'individual address',
}

prios = {
    LPDUDataFrame.PRIO_LOW: 'low',
    LPDUDataFrame.PRIO_NORMAL: 'normal',
    LPDUDataFrame.PRIO_SYSTEM: 'system',
    LPDUDataFrame.PRIO_URGENT: 'urgent',
}


def get_telegram_display(buf):
    lpdu = LPDUFrame.from_packet(buf.buffer)
    if isinstance(lpdu, LPDUDataFrame):
        return ('''repeated: {}
valid length: {}
valid checksum: {}
source: {}
destination address type: {}
destination: {}
hops: {}
priority: {}
tpdu_frame: {}
layer 4 raw data: {}''').format(
            lpdu.repeated,
            lpdu.valid_length,
            lpdu.valid_checksum,
            lpdu.source,
            addr_types[lpdu.addr_type],
            lpdu.destination,
            lpdu.hops,
            prios[lpdu.priority],
            lpdu.tpdu_frame().decode(),
            lpdu.data()
        )
    else:
        return lpdu.decode()


class EIBHandler(object):
    def __init__(self, url, frontend):
        self._ioloop = tornado.ioloop.IOLoop.instance()
        self.frontend = frontend
        self.keep_running = True
        self.fd = None
        self.fd_is_open = False
        self.url = url
        super(EIBHandler, self).__init__()

    @gen.coroutine
    def wait_fd(self):
        future = Future()
        self._ioloop.add_handler(self.fd,
                                 lambda *args: future.set_result(None),
                                 self._ioloop.READ)
        self.fd_is_open = True
        yield future
        if self.fd_is_open:
            self._ioloop.remove_handler(self.fd)
            self.fd_is_open = False

    @gen.coroutine
    def fetch_all(self):
        conn = EIBConnection()
        buf = EIBBuffer()

        # open socket
        if conn.EIBSocketURL(self.url) == -1:
            raise RuntimeError('Connection open failed')

        self.fd = conn.EIB_Poll_FD().fileno()

        # request open bus monitor
        if conn.EIBOpenBusmonitor_async() == -1:
            raise RuntimeError('Open bus monitor request failed')

        while self.keep_running:
            yield self.wait_fd()
            res = conn.EIB_Poll_Complete()
            if res == 1:
                conn.EIBComplete()
                break
            elif res == -1:
                raise RuntimeError('Could not poll open bus monitor')

        # request data
        while self.keep_running:
            conn.EIBGetBusmonitorPacket_async(buf)
            yield self.wait_fd()
            res = conn.EIB_Poll_Complete()
            if res == 1:
                conn.EIBComplete()
                self.frontend.process_telegram(get_telegram_display(buf))
            elif res == -1:
                raise RuntimeError('Could not poll bus monitor packet')

    def close(self):
        self.keep_running = False
        if self.fd_is_open:
            self._ioloop.remove_handler(self.fd)

