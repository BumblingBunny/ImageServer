import os

class FileHandler(object):
    CONTENT_TYPE = {
        "png": "image/png",
        "jpeg": "image/jpeg",
        "jpg": "image/jpeg",
        "html": "text/html",
        "css": "text/css",
        }
    def __init__(self, baseurl, options, lock):
        self.docroot = options["docroot"]
        self.index = options["index"]
        if "refresh" in options:
            self.refresh = options['refresh']
        else:
            self.refresh = -1

    def infer_content_type(self, req, target):
        f_ext = target.rsplit(".")[-1]
        if f_ext in self.CONTENT_TYPE:
            req.content_type(self.CONTENT_TYPE[f_ext])
        else:
            req.content_type("octet-stream")
        
    def handle(self, req, args):
        bare, flags = req.argsplit(args)
        if not bare or not bare[0]:
            target = self.index
        else:
            target = bare[0]

        # Ensure the target is in the right location to prevent
        # fs traversal
        target = os.path.abspath(os.path.join(self.docroot, target))
        if not target.startswith(self.docroot):
            req.send_error(404)
            return

        if not os.path.exists(target):
            req.send_error(404)
            return

        req.send_response(200)
        self.infer_content_type(req, target)
        
        if self.refresh > 0:
            req.refresh(self.refresh)
        req.start_response()

        req.wfile.write(open(target, 'r').read())


