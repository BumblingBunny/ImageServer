from BaseHandler import BaseHandler
import Camera
import ImageAnnotator

class CameraHandler(BaseHandler):
    def __init__(self, baseurl, options, lock):
        self.lock = lock()
        camera_mod = "Camera"
        annotator = "ImageAnnotator"
        vflip = False
        hflip = False
        resolution = (1024, 768)

        if "camera" in options:
            camera_mod = options["camera"]
        if "annotator" in options:
            annotator = options["annotator"]
        if "vflip" in options:
            vflip = options["vflip"] == "yes"
        if "hflip" in options:
            hflip = options["hflip"] == "yes"
        if "resolution" in options:
            resolution = [int(x) for x in options["resolution"].split("x")]

        self.camera = getattr(Camera, camera_mod)(vflip=vflip, hflip=hflip, resolution=resolution)
        self.annotator = getattr(ImageAnnotator, annotator)

    def handle(self, req, args):
        if not args or not args[0]:
            with self.lock:
                req.image_response(self.annotator(self.camera.quickshot()).annotate())
            return

        bare, flags = req.argsplit(args)
        if not bare or not bare[0]:
            with self.lock():
                req.image_response(self.annotator(self.camera.snapshot(**flags)).annotate())
        else:
            if bare[0] == "on":
                req.text_response(self.camera.on(), "plain")
            elif bare[1] == "off":
                req.text_response(self.camera.off(), "plain")
            else:
                req.send_error(404)
