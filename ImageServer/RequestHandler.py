import BaseHTTPServer
import os
from ConfigParser import ConfigParser

"""
This implements the general request "routing" and ties the various
bits that create data together. It also handles authentication.

The config contains sections called [handler:xyz]. This registers a
handler for any request to /xyz/ or below to be handled by the class
"module" (optionally sourced from library "location", defaulting to
the same name as "module") in that section. Additional config for the
handler classes can be placed in the config section.

Note that only the first path element of a URL will ever be matched,
e.g. [handler:mrtg/images] would never match, instead RequestHandler
would look for a handler matchig "mrtg".
"""


## G_CONFIG is deleted once initial configuration is complete
G_CONFIG = None

## G_HANDLERS maps "base" bits of URLs to their handlers
G_HANDLERS = {}

# Configure and load plugins
def load_config():
    global G_CONFIG

    G_CONFIG = ConfigParser()
    G_CONFIG.read(os.path.expanduser("~/.plug/web.conf"))
load_config()

# Configure parallelism. Plugins may need to know how to synchronise
# their actions and thus need a locking mechanism, hence configure
# this before loading the modules.
if not "parallel" in G_CONFIG.options("baseconfig"):
    print "Running without parallelism"
    class ParallelMixIn:
        pass
    class Lock:
        def __enter__(self):
            return None
        def __exit__(self, type, value, traceback):
            pass
else:
    if G_CONFIG.get("baseconfig", "parallel") == "threading":
        print "Using threading"
        from SocketServer import ThreadingMixIn as ParallelMixIn
        from threading import Lock
    elif G_CONFIG.get("baseconfig", "parallel") == "forking":
        print "Using multi-processing"
        from SocketServer import ForkingMixIn as ParallelMixIn
        from multiprocessing import Lock
    else:
        raise ValueError("No such parallel model: %s" % (HOW_TO_PARALLEL))

# Load the handlers
def load_modules():
    global G_HANDLERS
    for section in [x for x in G_CONFIG.sections() if x.startswith("handler:")]:
        baseurl = section.split(":", 1)[1]
        mod_name = G_CONFIG.get(section, "module")
        if "location" in G_CONFIG.options(section):
            location = G_CONFIG.get(section, "location")
        else:
            location = mod_name

        print "Loading handler", mod_name, "for", baseurl
        mod = __import__(mod_name, globals(), locals(), [], -1)
        options = dict([(x, G_CONFIG.get(section, x)) for x in G_CONFIG.options(section)])
        G_HANDLERS[baseurl] = getattr(mod, mod_name)(baseurl=baseurl, options=options, lock=Lock)
load_modules()

del G_CONFIG

class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def version_string(self):
        """ Disguise software used """
        return "GNU Terry Pratchet"

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

    def text_response(self, text, encoding="html"):
        self.send_response(200)
        self.content_type("text/%s" % (encoding))
        self.start_response()
        self.wfile.write(text)

    def image_response(self, data, encoding="jpeg"):
        self.send_response(200)
        self.content_type("image/%s" % (encoding.lower()))
        self.start_response()
        self.wfile.write(data)

    def redirect_response(self, target, text="And now for something completely different..."):
        self.send_response(303)
        self.send_header("Location", target)
        self.start_response()
        self.wfile.write(text)

    def auth(self):
        """ Ensure all requests are authenticated properly """
        if self.headers.getheader('Authorization') is None:
            self.require_auth()
            return False
        elif self.headers.getheader('Authorization') == "Basic ******************"
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

        if path[0] in G_HANDLERS:
            G_HANDLERS[path[0]].handle(self, path[1:])
            return
        else:
            self.send_error(404)


def serve(port=8008):
    class ParallelHTTPServer(ParallelMixIn, BaseHTTPServer.HTTPServer):
        pass

    httpd = ParallelHTTPServer(("", port), RequestHandler)
    print "Online"
    try:
        httpd.serve_forever()
    except:
        print "Forced shut down"
        httpd.server_close()
        raise

    httpd.server_close()
    return 0
