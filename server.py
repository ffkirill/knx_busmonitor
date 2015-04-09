#!-*- coding: utf-8 -*-
import re
import os
import uuid

from functools import partial
import datetime

import tornado.web
import tornado.ioloop
import tornado.websocket
from tornado import gen
from tornado_subprocess import Subprocess
from tornado.concurrent import Future

from eibhandler import EIBHandler

from tornado.options import define, options, parse_command_line

define("address", default="", help="listen address", type=str)
define("port", default=8888, help="run on the given port", type=int)
define("debug", default=False, help="run in debug mode")


def is_valid_hostname(hostname):
    if len(hostname) > 255:
        return False
    if hostname[-1] == ".":
        hostname = hostname[:-1] # strip exactly one dot from the right, if present
    allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
    return all(allowed.match(x) for x in hostname.split("."))


class WebSocket(tornado.websocket.WebSocketHandler):
    subprocess = None
    socket_path = None
    backend = None

    def data_received(self, chunk):
        pass

    def on_message(self, message):
        pass

    def on_subprocess_exit(self, *args):
        try:
            os.remove(self.socket_path)
        except:
            pass

    @gen.coroutine
    def open(self, remote_host):
        hostname, sep, port = remote_host.rpartition(':')
        if not is_valid_hostname(hostname) or not re.match(r'\d+', port):
            self.write_message('invalid connection string')
            self.close()
            raise gen.Return()
        self.socket_path = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            str(uuid.uuid4()))
        self.subprocess = Subprocess(
            self.on_subprocess_exit,
            args=['eibd', 'iptn:{}:{}'.format(hostname, port),
                  '--listen-local={}'.format(self.socket_path)])
        self.subprocess.start()
        f = Future()
        # TODO: fix this crap
        tornado.ioloop.IOLoop.instance().add_timeout(
            datetime.timedelta(seconds=3), partial(f.set_result, None))
        yield f
        self.backend = EIBHandler('local:{}'.format(self.socket_path), self)
        yield self.backend.fetch_all()

    def on_close(self, message=None):
        self.backend.close()
        del self.backend
        self.subprocess.cancel()
        del self.subprocess

    def process_telegram(self, data):
        self.write_message(data)


def main():
    parse_command_line()
    app = tornado.web.Application(
        [
            (r'/websocket/(.*)', WebSocket),
            ],
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        debug=options.debug,
        )
    app.listen(options.port, address=options.address)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()