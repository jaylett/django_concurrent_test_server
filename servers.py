import BaseHTTPServer
import SocketServer
import random
import time

from django.core.servers.basehttp import WSGIServer, WSGIRequestHandler
from django.conf import settings

class RandomWaitMixin(object):
    def process_request(self, *args, **kwargs):
        if getattr(settings, 'CONCURRENT_RANDOM_DELAY', None):
            time.sleep(random.random()/3)
        return super(RandomWaitMixin, self).process_request(*args, **kwargs)

class ThreadedServer(RandomWaitMixin, SocketServer.ThreadingMixIn, WSGIServer):
    def __init__(self, server_address, RequestHandlerClass=None):
         BaseHTTPServer.HTTPServer.__init__(self, server_address, RequestHandlerClass)

class ForkedServer(RandomWaitMixin, SocketServer.ForkingMixIn, WSGIServer):
    def __init__(self, server_address, RequestHandlerClass=None):
        BaseHTTPServer.HTTPServer.__init__(self, server_address, RequestHandlerClass)

def run(addr, port, wsgi_handler):
    server_address = (addr, port)
    if hasattr(settings, 'USE_MULTITHREADED_SERVER'):
        threaded = settings.USE_MULTITHREADED_SERVER
    else:
        threaded = False
    if hasattr(settings, 'USE_MULTIFORKED_SERVER'):
        forked = settings.USE_MULTIFORKED_SERVER
    else:
        forked = False
    if threaded:
        httpd = ThreadedServer(server_address, WSGIRequestHandler)
    elif forked:
        httpd = ForkedServer(server_address, WSGIRequestHandler)
    else:
        httpd = WSGIServer(server_address, WSGIRequestHandler)
    httpd.set_app(wsgi_handler)
    httpd.serve_forever()
