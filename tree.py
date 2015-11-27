import sys
import os

HOW_TO_PARALLEL = "threading"

if "HOW_TO_PARALLEL" in os.environ:
    HOW_TO_PARALLEL = os.environ['HOW_TO_PARALLEL']
else:
    os.environ["HOW_TO_PARALLEL"] = HOW_TO_PARALLEL

from ImageServer.CameraHandler import serve

if "TREEBUG" in os.environ:
    import time
    from cProfile import Profile
    import pstats
    from StringIO import StringIO

def main():
    if "TREEBUG" in os.environ:
        last_int = 0
        prof = Profile()
        while True:
            prof.enable()
            try:
                serve()
            except KeyboardInterrupt:
                if time.time() - last_int < 1:
                    break
                prof.disable()
                output = StringIO()
                ps = pstats.Stats(prof, stream=output).sort_stats("cumulative")
                ps.print_stats()
                print "\n".join([line for line in output.getvalue().splitlines() \
                                     if not ( "/usr/lib" in line or "{" in line )])
                output.close()
                prof = Profile()
                last_int = time.time()
    else:
        serve()
if __name__ == "__main__":
    main()
