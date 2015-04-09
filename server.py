#!-*- coding: utf-8 -*-
import re
import os
import uuid

from functools import partial
import datetime

import memcache

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

MEMCACHE_SERVERS = (
    '127.0.0.1:11211',
)
MEMCACHE_PORT_KEY = 'knx_busmonitor_port'
EIDB_STARTING_PORT = 3671


def is_valid_hostname(hostname):
    if not hostname.strip() or len(hostname) > 255:
        return False
    if hostname[-1] == ".":
        hostname = hostname[:-1] # strip exactly one dot from the right, if present
    allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
    return all(allowed.match(x) for x in hostname.split("."))


class WebSocket(tornado.websocket.WebSocketHandler):
    subprocess = None
    socket_path = None
    backend = None
    is_open = False
    port_num = None

    def data_received(self, chunk):
        pass

    def _response(self, **kwargs):
        if self.is_open:
            msg = {'timeStamp': str(datetime.datetime.today()),
                   'messageType': 'info'}
            msg.update(kwargs)
            self.write_message(msg)

    def error(self, message):
        self._response(messageType='error', message=message)

    def info(self, message):
        self._response(messageType='info', message=message)

    def on_message(self, message):
        pass

    def on_subprocess_exit(self, status, stdout, stderr):
        self.release_port()
        self.error('EIBD unexpected termination: {} {}'.format(stderr, stdout))
        try:
            os.remove(self.socket_path)
        except:
            pass
        self.close()

    def acquire_port(self):
        num = EIDB_STARTING_PORT
        while not self.application.memcache_connection.add(
                '{}_{}'.format(MEMCACHE_PORT_KEY, num), ''):
            num += 1
        return num

    def release_port(self):
        self.application.memcache_connection.delete('{}_{}'.format(
            MEMCACHE_PORT_KEY, self.port_num))

    @gen.coroutine
    def open(self, remote_host):
        self.is_open = True
        try:
            hostname, sep, port = remote_host.rpartition(':')
            if not is_valid_hostname(hostname) or not re.match(r'\d+', port):
                self.error('invalid connection string')
                self.close()
                raise gen.Return()
            self.socket_path = os.path.join(
                os.path.abspath(os.path.dirname(__file__)),
                str(uuid.uuid4()))
            self.port_num = self.acquire_port()
            self.subprocess = Subprocess(
                self.on_subprocess_exit,
                args=['eibd', 'iptn:{}:{}:{}'.format(hostname, port,
                                                     self.port_num),
                      '--listen-local={}'.format(self.socket_path)])
            self.subprocess.start()
            f = Future()
            # TODO: fix this crap
            tornado.ioloop.IOLoop.instance().add_timeout(
                datetime.timedelta(seconds=3), partial(f.set_result, None))
            yield f
            self.backend = EIBHandler('local:{}'.format(self.socket_path), self)
            yield self.backend.fetch_all()
        except Exception as e:
            self.error(str(e))

    def on_close(self, message=None):
        self.is_open = False
        if self.backend:
            self.backend.close()
            del self.backend
        if self.subprocess:
            self.subprocess.callback = lambda *args: self.on_subprocess_exit(
                0, '', '')
            self.subprocess.cancel()
            del self.subprocess

    def process_telegram(self, data):
        self.write_message(data)


class Application(tornado.web.Application):
    def __init__(self, handlers=None, default_host="", transforms=None,
                 **settings):
        self.memcache_connection = memcache.Client(MEMCACHE_SERVERS)
        super(Application, self).__init__(handlers, default_host, transforms,
                                          **settings)


def main():
    parse_command_line()
    app = Application(
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