import os
import time
from PlugD import PlugD
from PlugDImageAnnotator import PlugIcon
from StringIO import StringIO
from Sensors import hum_tem

class PlugDHandler(object):
    def __init__(self):
        self.plug = PlugD()

    def html(self):
        html = os.path.expanduser("~/.plug/toggle_index.html")
        if not os.path.exists(html):
            return ""

        result = StringIO()
        with open(os.path.expanduser("~/.plug/toggle_index.html")) as fh:
            for line in fh:
                if "##PLUG_IMAGES##" in line:
                    self.button_list(result)
                elif "##HUM_TEM##" in line:
                    self.add_environment(result)
                else:
                    result.write(line)
        return result.getvalue()


    def button_list(self, output):
        states = self.plug.status()
        for state in states:
            output.write("<a class=\"plug_button\" href=\"toggle/"+state.name+"\">")
            output.write("<img class=\"plug_icon\" src=\"icon/"+state.name+"\" alt=\""+state.name+"\" /></a>")

    def add_environment(self, output):
        output.write(time.strftime("%H:%M ") + " ".join(hum_tem()))

    def icon(self, name, encoding="PNG"):
        states = self.plug.status()
        wanted = [state for state in states if state.name == name]
        if len(wanted) != 1:
            return None
        return PlugIcon(wanted[0]).to_binary(encoding=encoding)

    def command(self, com, target):
        com_table = {
            "on": "enable",
            "off": "disable",
            "toggle": "toggle"
            }
        if com not in com_table:
            return False
        com = com_table[com]
        
        states = self.plug.status()
        if len([state for state in states if state.name == target]) != 1:
            return False
        result = getattr(self.plug, com)(target)
        if result is None:
            return False
        return True

    def css(self, bare):
        css = os.path.expanduser("~/.plug/toggle_index.css")
        if os.path.exists(css):
            return open(css, 'r').read()
        else:
            return ""
