#!-*- coding: utf-8 -*-
import tornado.web
import tornado.ioloop
import tornado.websocket
from tornado import gen

from eibhandler import EIBHandler


class WebSocket(tornado.websocket.WebSocketHandler):
    def data_received(self, chunk):
        pass

    def on_message(self, message):
        pass

    @gen.coroutine
    def open(self):
        self.application.ws_connections.add(self)
        self.backend = EIBHandler(self)
        yield self.backend.fetch_all()

    def on_close(self, message=None):
        self.backend.close()
        del self.backend
        self.application.ws_connections.remove(self)

    def process_telegram(self, data):
        self.write_message(data)


class Application(tornado.web.Application):
    def __init__(self):
        self.ws_connections = set()

        handlers = (
            (r'/(index\.html)', tornado.web.StaticFileHandler,  {'path': '.'}),
            (r'/websocket/?', WebSocket),
        )

        tornado.web.Application.__init__(self, handlers)


application = Application()

if __name__ == '__main__':
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
