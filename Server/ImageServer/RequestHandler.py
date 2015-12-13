import BaseHTTPServer
import os
from ConfigParser import ConfigParser

"""
Modular request handler.

The config contains sections called [handler:xyz]. This registers a
handler for any request to /xyz/ or below to be handled by the class
"module" (optionally sourced from library "location", defaulting to
the same name as "module") in that section. Additional config for the
handler classes can be placed in the config section.

Note that only the first path element of a URL will ever be matched,
e.g. [handler:mrtg/images] would never match, instead RequestHandler
would look for a handler matchig "mrtg".
"""

class RQError(Exception):
    pass


## G_CONFIG is deleted once initial configuration is complete
G_CONFIG = None

## G_HANDLERS maps "base" bits of URLs to their handlers. This global
## is the easy way around BaseHTTPRequestHandler's stateless,
## init-less nature.
G_HANDLERS = {}

## Load config
def load_config():
    global G_CONFIG

    G_CONFIG = ConfigParser()
    G_CONFIG.read(os.path.expanduser("~/.plug/web.conf"))
load_config()

## Configure parallelism. Plugins may need to know how to synchronise
## their actions and thus need a locking mechanism, hence configure
## this before loading the modules.
if not "parallel" in G_CONFIG.options("baseconfig"):
    print "Running without parallelism, set \"parallel\" in the baseconfig to fix this"
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
        raise RQError("No such parallel model: %s" % (G_CONFIG.get("baseconfig", "parallel")))


## Load the handlers
def get_module(section):
    mod_name = G_CONFIG.get(section, "module")
    mod_location = mod_name
    if "location" in G_CONFIG.options(section):
        mod_location = G_CONFIG.get(section, "location")
    mod_loc = __import__(mod_location, globals(), locals(), [], -1)

    mod = getattr(mod_loc, mod_name)
    options = dict([(x, G_CONFIG.get(section, x)) for x in G_CONFIG.options(section)])
    return mod, options


def load_modules():
    global G_HANDLERS
    ## auth module
    print "Loading auth module"
    mod, options = get_module("auth")
    try:
        G_HANDLERS["__auth__"] = mod(**options)
    except Exception as err:
        raise RQError("Auth init failed: " + str(err))

    ## handler modules
    for section in [x for x in G_CONFIG.sections() if x.startswith("handler:")]:
        baseurl = section.split(":", 1)[1]
        print "Loading", section
        try:
            mod, options = get_module(section)
            G_HANDLERS[baseurl] = mod(baseurl=baseurl, options=options, lock=Lock)
        except Exception as err:
            raise RQError("Failed to load module: " + str(err))

load_modules()
del G_CONFIG


class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self._header_stash = {}
        BaseHTTPServer.BaseHTTPRequestHandler.__init__(self, *args, **kwargs)

    def version_string(self):
        """ Disguise software used """
        return "GNU Terry Pratchet"

    ## Utilities
    def nocache(self):
        """ Advise against caching """
        self._header_stash["Cache-Control"] = "no-cache, no-store, must-revalidate"
        self._header_stash["Pragma"] = "no-cache"
        self._header_stash["Expires"] = 0

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
        self._header_stash["Refresh"] = refresh_time

    def start_response(self):
        """ Alias for end_headers, wrapped in case I want to add
        certain headers on all requests """
        for header, value in self._header_stash.items():
            self.send_header(header, value)
        self.end_headers()

    def content_type(self, c_type="image/jpeg"):
        """ Short hand to set the content type """
        self._header_stash["Content-Type"] = c_type

    def text_response(self, text, encoding="html"):
        """
        Convenience function to send a text response. Defaults to HTML
        as content type.
        """
        self.send_response(200)
        self.content_type("text/%s" % (encoding))
        self.start_response()
        self.wfile.write(text)

    def image_response(self, data, encoding="jpeg"):
        """
        Convenience function to send an image response, defaults to
        JPEG as content type.
        """
        self.send_response(200)
        self.content_type("image/%s" % (encoding.lower()))
        self.start_response()
        self.wfile.write(data)

    def redirect_response(self, target, text="And now for something completely different..."):
        """
        Convenience method for a 303 redirect response
        """
        self.send_response(303)
        self.send_header("Location", target)
        self.start_response()
        self.wfile.write(text)

    def do_GET(self):
        if G_HANDLERS["__auth__"].handle(self) is not True:
            G_HANDLERS["__auth__"].auth_required_response(self)
            return

        path = self.path.split("/")[1:]

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
