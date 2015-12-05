import BaseHTTPServer
import os
import urllib
from ImageAnnotator import PlugDImageAnnotator as ImageAnnotator
from PlugDHandler import PlugDHandler
from Camera import HumTemCamera as Camera
from Sensors import hum_tem

"""
This implements the general request "routing" and ties the various
bits that create data together. It also handles authentication.

This works as follows:

A request for /mrtg/mrtg.css is split on "/":
["mrtg", "mrtg.css"]

The first element is consumed to determine the handler (handle_mrtg)
which is called with the remainder of the split result as an
argument. Its up to that function to further process args.

The error pages when things go wrong and general behaviour is designed
to disguise internal errors and make content discovery more difficult.

TreeHandler has grown quite a bit, perhaps it should be split up soon.
"""

# Avoid instantiating the camera over-and-over again, instead keep it
# as a module global.
G_CAMERA = Camera(vflip=True, hflip=True)

if not "HOW_TO_PARALLEL" in os.environ:
    raise ValueError("Environment improperly configured")


if os.environ["HOW_TO_PARALLEL"] == "threading":
    print "Using threading"
    from SocketServer import ThreadingMixIn as ParallelMixIn
    from threading import Lock
    from threading import current_thread
    id_finder = lambda: current_thread().ident
elif os.environ["HOW_TO_PARALLEL"] == "forking":
    print "Using multi-processing"
    from SocketServer import ForkingMixIn as ParallelMixIn
    from multiprocessing import Lock
    id_finder = os.getpid
else:
    raise ValueError()


G_LOCKS = {}
G_LOCKS_LOCK = Lock()


def serialize(lock_group):
    """
    Serialize access to certain "groups" of functions.
    """
    global G_LOCKS

    if not lock_group in G_LOCKS:
        with G_LOCKS_LOCK:
            if not lock_group in G_LOCKS:
                G_LOCKS[lock_group] = Lock()

    def curried_serialize(func):
        def wrapper(*args, **kwargs):
            with G_LOCKS[lock_group]:
                result = func(*args, **kwargs)
            return result
        return wrapper
    return curried_serialize


class TreeHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    # Utilities
    def nocache(self):
        """ Advise against caching """
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")

    def argsplit(self, args):
        """ Takes a list of arguments and splits them into "bare"
        arguments (those which don't look like k/v pairs) and "flags",
        those that do. Flags are translated into a dict."""
        bare = []
        flags = {}

        for arg in args:
            if not "=" in arg:
                bare.append(arg)
            else:
                key, value = arg.split("=", 1)
                flags[key] = value
        return bare, flags

    def refresh(self, refresh_time=5):
        """ Advise a refresh, by default after 5 seconds"""
        self.send_header("Refresh", refresh_time)

    def start_response(self):
        """ Alias for end_headers, wrapped in case I want to add
        certain headers on all requests """
        self.end_headers()

    def content_type(self, c_type="image/jpeg"):
        """ Short hand to set the content type """
        self.send_header("Content-Type", c_type)

    # Function overrides, not do_*
    def version_string(self):
        """ Disguise software used """
        return "GNU Terry Pratchet"

    # Handlers
    def handle_(self, args=None):
        """ Base handler. Does nothing. """
        self.send_response(200)
        self.start_response()
        self.content_type("text/plain")
        self.wfile.write("GNU Terry Pratchet")
        return

    def handle_plugicon(self, args):
        """ Entry point for handling the "control centre" """
        bare, flags = self.argsplit(args)

        if not bare or not bare[0]:
            # No further path, show the index page
            self.send_response(200)
            self.refresh(30)
            self.content_type("text/html")
            self.start_response()
            self.wfile.write(PlugDHandler().html())
        else:
            if bare[0] == "icon":
                self.handle_plugicon_icon(bare[1:], flags)
            elif bare[0] in ("on", "off", "toggle"):
                self.handle_plugicon_command(bare[0], bare[1:], flags)
            elif bare[0] == "css":
                self.handle_plugicon_css(bare[1:], flags)
            else:
                self.send_error(404)

    def handle_plugicon_icon(self, bare, flags):
        icon = urllib.unquote(bare[0])
        icon = PlugDHandler().icon(icon)
        if icon is None:
            print "No icon for", icon
            self.send_error(404)
        else:
            self.send_response(200)
            self.content_type("image/png")
            self.start_response()
            self.wfile.write(icon)

    @serialize("PlugD_RW")
    def handle_plugicon_command(self, com, bare, flags):
        if not bare or not bare[0]:
            self.send_error(400)
        else:
            target = urllib.unquote(bare[0])
            success = PlugDHandler().command(com, target)
            if success is True:
                self.send_response(303)
                self.send_header("Location", "/plugicon/")
                self.start_response()
                self.wfile.write("success")
            else:
                self.send_error(400)

    def handle_plugicon_css(self, bare, flags):
        self.send_response(200)
        self.content_type("text/css")
        self.start_response()
        self.wfile.write(PlugDHandler().css(bare))

    def handle_mrtg(self, args):
        bare, flags = self.argsplit(args)
        if not bare or not bare[0]:
            target = "humtem.html"
        else:
            target = bare[0]

        # Ensure the target is in the right location to prevent
        # fs traversal
        target = os.path.abspath(os.path.join("/home/pi/mrtg/", target))
        if not target.startswith("/home/pi/mrtg/"):
            self.send_error(404)
            return

        if not os.path.exists(target):
            print "no", target
            self.send_error(404)
            return

        self.send_response(200)
        if target.endswith("png"):
            self.content_type("image/png")
        elif target.endswith("html"):
            self.content_type("text/html")
        elif target.endswith("css"):
            self.content_type("text/css")
        else:
            self.content_type("octet-stream")
        self.refresh(600)
        self.start_response()

        self.wfile.write(open(target, 'r').read())

    def handle_snapshot(self, args):
        if not args:
            self.handle_snapshot_normal()
            return

        bare, flags = self.argsplit(args)
        try:
            self.handle_snapshot_with_parms(**flags)
        except TypeError:
            self.send_error(500)

    def handle_sensors(self, args):
        if not args:
            self.handle_sensors_default()
        else:
            self.send_error(404)

    def handle_sensors_default(self):
        try:
            hum, tem = hum_tem()
        except:
            self.send_error(500)
            return

        self.send_response(200)
        self.nocache()
        self.content_type("text/plain")
        self.refresh(10)
        self.start_response()

        self.wfile.write("RH: %s\r\nT : %s\r\n" % (hum, tem))

    def handle_snapshot_normal(self):
        self.send_response(200)
        self.nocache()
        self.content_type()
        self.refresh(10)
        self.start_response()
        self.wfile.write(ImageAnnotator(G_CAMERA.quickshot()).annotate())

    def handle_snapshot_with_parms(self, **kwargs):
        self.send_response(200)
        self.nocache()
        self.content_type()
        self.refresh(60)
        self.start_response()

        self.wfile.write(G_CAMERA.snapshot(**kwargs))

    # Disable/enable camera. Useful when trying to experiment with the
    # camera outside of this system without shutting everything else
    # down
    def handle_off(self):
        self.send_response(200)
        self.content_type("text/plain")
        self.wfile.write(G_CAMERA.off())

    def handle_on(self):
        self.send_response(200)
        self.content_type("text/plain")
        self.wfile.write(G_CAMERA.on())

    def auth(self):
        """ Ensure all requests are authenticated properly """
        if self.headers.getheader('Authorization') is None:
            self.require_auth()
            return False
        elif self.headers.getheader('Authorization') == "Basic ****************":
            return True
        else:
            self.require_auth()
            return False
        return False

    def require_auth(self):
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm=\"Mon\"')
        self.content_type('text/plain')
        self.start_response()
        self.wfile.write("GNU Terry Pratchet")

    def do_GET(self):
        if not self.auth() is True:
            return

        path = self.path.split("/")[1:]
        if "_" in path[0]:
            self.return_error(404)

        handler = "handle_%s" % (path[0])
        if hasattr(self, handler):
            handler_func = getattr(self, handler)
            if not callable(handler_func):
                self.send_error(404)
            else:
                handler_func(args=path[1:])
        else:
            self.send_error(404)


def serve(port=8008):
    class ParallelHTTPServer(ParallelMixIn, BaseHTTPServer.HTTPServer):
        pass

    httpd = ParallelHTTPServer(("", port), TreeHandler)
    print "Online"
    try:
        httpd.serve_forever()
    except:
        print "Forced shut down"
        httpd.server_close()
        raise

    httpd.server_close()
    return 0
