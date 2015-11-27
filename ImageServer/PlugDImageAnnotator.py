import os
from PIL import Image, ImageDraw
from io import BytesIO
from cStringIO import StringIO
from PlugD import PlugD

class PlugIcon(object):
    def __init__(self, state, icon=None):
        self.image = None
        self.draw = None
        self.bound = (0,0, 31,31)

        if icon is None:
            if state.name.startswith("Empty "):
                icon = os.path.expanduser("~/.plug/Blank.png")
            else:
                icon = os.path.expanduser(os.path.join("~/.plug/", state.name + ".png"))

        if os.path.exists(icon):
            self.image = Image.open(icon)
        else:
            self.image = Image.new("RGB", (32,32), "white")
            self.draw = ImageDraw.Draw(img)
            if state.name == "Warm Light":
                self.draw.ellipse(self.bound, outline="rgb(0,0,0)", fill="rgb(255,255,0)")
            elif state.name == "Broken":
                pass
            elif state.name == "Daylight Light":
                self.draw.ellipse(self.bound, outline="rgb(0,0,0)", fill="rgb(255,255,255)")
            elif state.name == "Main Light":
                self.draw.chord(self.bound, 270, 90, outline="rgb(0,0,0)", fill="rgb(255,255,255)")
                self.draw.chord(self.bound, 90, 270, outline="rgb(0,0,0)", fill="rgb(255,255,0)")
            elif state.name == "Heater":
                self.draw.ellipse(self.bound, outline="rgb(0,0,0)", fill="rgb(200,0,0)")
            elif state.name == "Extractor":
                for i in (70, 190, 310):
                    self.draw.pieslice(self.bound, i, i+40, outline="rgb(0,0,0)", fill="rgb(200,200,200)")

        if not state.on:
            self.cross_out()
        
    def cross_out(self, icon=None):
        if icon is None:
            icon = os.path.expanduser(os.path.join("~/.plug/Off.png"))

        if os.path.exists(icon):
            icon = Image.open(icon)
            self.image.paste(icon, (0, 0), icon)
        else:
            self.draw.draw(bound, 315, 135, outline="rgb(255,0,0)")
            self.draw.draw(bound, 135, 315, outline="rgb(255,0,0)")

    def to_binary(self, encoding="JPEG"):
        result = StringIO()
        self.image.save(result, encoding)
        data = result.getvalue()
        result.close()
        return data
        

class PlugDImageAnnotator(object):
    def __init__(self, imgdata):
        self.image = Image.open(BytesIO(imgdata))
        self.draw = ImageDraw.Draw(self.image)
        self.plug = PlugD()

    def annotate(self, encoding="JPEG"):
        states = self.plug.status()
        y_pos = 0
        for state in states:
            icon = PlugIcon(state).image
            self.image.paste(icon, (0, y_pos), icon)
            y_pos += 32

        result = StringIO()
        self.image.save(result, encoding)
        return result.getvalue()
