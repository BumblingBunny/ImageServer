import picamera

from io import BytesIO
from fractions import Fraction
from time import strftime

try:
    from Sensors import hum_tem
except ImportError:
    pass

try:
    from PlugD import PlugD
except ImportError:
    pass

# Attributes in CAMERA_SETTINGS are reset after a function decorated
# with @preseve_state
CAMERA_SETTINGS = ["framerate", "shutter_speed", "exposure_mode", "iso", "hflip", "vflip", "annotate_text"]


def preserve_state(func):
    def wrapped(self, *args, **kwargs):
        backup = {}
        for setting in CAMERA_SETTINGS:
            if hasattr(self.camera, setting):
                backup[setting] = getattr(self.camera, setting)
        result = func(self, *args, **kwargs)
        for setting in CAMERA_SETTINGS:
            if hasattr(self.camera, setting) and setting in backup:
                setattr(self.camera, setting, backup[setting])
        return result
    return wrapped


class Camera(object):
    def __init__(self, hflip=False, vflip=False, resolution=(1024, 768)):
        self.vflip = vflip
        self.hflip = hflip
        self.resolution = resolution
        self.start_camera()
        self.image_cache = None

    def annotate_text(self):
        return strftime("%H:%M")

    def start_camera(self):
        self.camera = picamera.PiCamera()
        self.camera_open = True
        self.camera.resolution = self.resolution
        self.camera.vflip = self.vflip
        self.camera.hflip = self.hflip
        self.camera_open = True

    def off(self):
        if self.camera_open:
            self.camera.close()
            self.camera_open = False
            return "Camera closed"
        else:
            return "Camera already closed"

    def on(self):
        if not self.camera_open:
            self.start_camera()
            return "Camera started"
        else:
            return "Camera already started"

    def status(self):
        result = "Camera status: "
        if self.camera_open:
            result += "ON"
        else:
            result += "OFF"
        return result

    @preserve_state
    def quickshot(self):
        img = BytesIO()
        self.camera.annotate_text = self.annotate_text()
        self.camera.capture(img, format="jpeg")
        return img.getvalue()

    @preserve_state
    def snapshot(self, framerate=Fraction(1, 6), shutter_speed=6000000, exposure_mode="off", iso=800):
        img = BytesIO()
        self.camera.framerate = framerate
        self.camera.shutter_speed = shutter_speed
        self.camera.exposure_mode = exposure_mode
        self.camera.iso = iso
        self.camera.annotate_text = self.annotate_text()
        self.camera.capture(img, "jpeg")

        return img.getvalue()


class HumTemCamera(Camera):
    def __init__(self, *args, **kwargs):
        super(HumTemCamera, self).__init__(*args, **kwargs)
        self.plug = PlugD()

    def quickshot(self):
        if self.plug.lights_on():
            return super(HumTemCamera, self).quickshot()
        else:
            return self.snapshot()

    def annotate_text(self):
        return "%s %s" % ((super(HumTemCamera, self).annotate_text(), " ".join(hum_tem())))
