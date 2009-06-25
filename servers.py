from django.core.servers.basehttp import WSGIServer, WSGIRequestHandler
from django.conf import settings
import BaseHTTPServer, SocketServer

class ThreadedServer(SocketServer.ThreadingMixIn, WSGIServer):
    def __init__(self, server_address, RequestHandlerClass=None):
         BaseHTTPServer.HTTPServer.__init__(self, server_address, RequestHandlerClass)

class ForkedServer(SocketServer.ForkingMixIn, WSGIServer):
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
