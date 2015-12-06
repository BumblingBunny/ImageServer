import os
from PIL import Image, ImageDraw
from io import BytesIO
from cStringIO import StringIO
from PlugD import PlugD


class PlugIcon(object):
    def __init__(self, state, icon=None):
        self.image = None
        self._draw = None

        if icon is None:
            if state.name.startswith("Empty "):
                icon = os.path.expanduser("~/.plug/Blank.png")
            else:
                icon = os.path.expanduser(os.path.join("~/.plug/", state.name + ".png"))

        if os.path.exists(icon):
            self.image = Image.open(icon)
        else:
            self.image = Image.new("RGB", (32, 32), "white")
            if state.name == "Warm Light":
                self.draw.ellipse(self.bound(), outline="rgb(0,0,0)", fill="rgb(255,255,0)")
            elif state.name == "Broken":
                pass
            elif state.name == "Daylight Light":
                self.draw.ellipse(self.bound(), outline="rgb(0,0,0)", fill="rgb(255,255,255)")
            elif state.name == "Main Light":
                self.draw.chord(self.bound(), 270, 90, outline="rgb(0,0,0)", fill="rgb(255,255,255)")
                self.draw.chord(self.bound(), 90, 270, outline="rgb(0,0,0)", fill="rgb(255,255,0)")
            elif state.name == "Heater":
                self.draw.ellipse(self.bound(), outline="rgb(0,0,0)", fill="rgb(200,0,0)")
            elif state.name == "Extractor":
                for i in (70, 190, 310):
                    self.draw.pieslice(self.bound(), i, i + 40, outline="rgb(0,0,0)", fill="rgb(200,200,200)")

        if not state.on:
            self.cross_out()

    def bound(self):
        return (0, 0) + self.image.size

    @property
    def draw(self):
        if self._draw is None:
            self._draw = ImageDraw.Draw(self.image)
        return self._draw

    def cross_out(self, icon=None):
        if icon is None:
            icon = os.path.expanduser(os.path.join("~/.plug/Off.png"))

        if os.path.exists(icon):
            icon = Image.open(icon)
            self.image.paste(icon, (0, 0), icon)
        else:
            self.draw.line(self.bound(), fill='rgb(255,0,0)')
            imsize = self.image.size
            self.draw.line((0, imsize[1], imsize[0], 0), fill='rgb(255,0,0)')

    def to_binary(self, encoding="JPEG"):
        result = BytesIO()
        self.image.save(result, encoding)
        data = result.getvalue()
        result.close()
        return data


class ImageAnnotator(object):
    def __init__(self, imgdata):
        self.image = Image.open(BytesIO(imgdata))

    def _encode(self, encoding):
        # StringIO used here instead of BytesIO, as BytesIO doesn't
        # support fileno
        result = StringIO()
        self.image.save(result, encoding)
        data = result.getvalue()
        result.close()
        return data

    def annotate(self, encoding="JPEG"):
        return self._encode(encoding=encoding)


class PlugDImageAnnotator(ImageAnnotator):
    def __init__(self, imgdata):
        super(PlugDImageAnnotator, self).__init__(imgdata)
        self.plug = PlugD()

    def annotate(self, encoding="JPEG"):
        states = self.plug.status()
        y_pos = 0
        for state in states:
            icon = PlugIcon(state).image
            self.image.paste(icon, (0, y_pos), icon)
            y_pos += icon.size[1]
        return self._encode(encoding=encoding)
