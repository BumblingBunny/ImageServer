import sys
import os
from ConfigParser import ConfigParser

from ImageServer.RequestHandler import serve


if "TREEBUG" in os.environ:
    import time
    from cProfile import Profile
    import pstats
    from StringIO import StringIO


def main():
    config = ConfigParser()
    try:
        config.read(os.path.expanduser("~/.plug/web.conf"))
    except Exception as err:
        print "Failed to parse config:", str(err)
        return 1

    port = 8008

    if "baseconfig" in config.sections() and "port" in config.options("baseconfig"):
        port = int(config.get("baseconfig", "port"))

    if "TREEBUG" in os.environ:
        last_int = 0
        prof = Profile()
        while True:
            prof.enable()
            try:
                serve(port=8008)
            except KeyboardInterrupt:
                if time.time() - last_int < 1:
                    break
                prof.disable()
                output = StringIO()
                ps = pstats.Stats(prof, stream=output).sort_stats("cumulative")
                ps.print_stats()
                print "\n".join([line for line in output.getvalue().splitlines()
                                 if not ("/usr/lib" in line or "{" in line)])
                output.close()
                prof = Profile()
                last_int = time.time()
    else:
        serve(port=port)

if __name__ == "__main__":
    sys.exit(main())
