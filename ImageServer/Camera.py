import picamera

from io import BytesIO
from fractions import Fraction
from time import sleep, strftime

from Sensors import hum_tem
from PlugD import PlugD

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
        self.plug = PlugD()

    def _annotate_text(self):
        return strftime("%H:%M ") + " ".join(hum_tem())

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
        if self.plug.lights_on():
            img = BytesIO()
            self.camera.annotate_text = self._annotate_text()
            self.camera.capture(img, format="jpeg")
            return img.getvalue()
        else:
            return self.snapshot()
    
    @preserve_state
    def snapshot(self, framerate = Fraction(1, 6), shutter_speed = 6000000, exposure_mode="off", iso=800):
        img = BytesIO()
        self.camera.framerate = framerate
        self.camera.shutter_speed = shutter_speed
        self.camera.exposure_mode = exposure_mode
        self.camera.iso = iso 
        self.camera.annotate_text = self._annotate_text()
        self.camera.capture(img, "jpeg")

        return img.getvalue()
