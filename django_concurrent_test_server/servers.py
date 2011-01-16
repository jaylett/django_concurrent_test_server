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
        
    def finish_request(self, request, client_address):
        # the process created by ForkingMixin.process_request will be used solely to
        # run a single leg of that method, which basically calls *this* method then
        # handles an error if necessary, and exits. It *should* drop its reference
        # to the listening socket at the start of the child process, but it doesn't.
        # This is the most convenient way of monkeypatching it in.
        #
        # Not dropping the socket means that if the listening process wants to reopen
        # the socket (which happens in Django's test server if code reloading is on)
        # then *any* still-running child process will cause that operation to fail. Django
        # can't recover from this at the moment; the child processes hang around (and
        # have to be killed manually), while the parent dies. Let's avoid that.
        self.socket.close()
        return super(SocketServer.ForkingMixIn, self).finish_request(request, client_address)

def run(addr, port, wsgi_handler):
    server_address = (addr, port)
    threaded = True # else forked
    if hasattr(settings, 'CONCURRENT_THREADING'):
        threaded = settings.CONCURRENT_THREADING
    if threaded:
        httpd = ThreadedServer(server_address, WSGIRequestHandler)
    else:
        httpd = ForkedServer(server_address, WSGIRequestHandler)
    httpd.set_app(wsgi_handler)
    httpd.serve_forever()
