import os
import time
from PlugD import PlugD
from ImageAnnotator import PlugIcon
from StringIO import StringIO
from Sensors import hum_tem
import urllib
from BaseHandler import BaseHandler, needs_args

class ControlCenter(BaseHandler):
    def __init__(self, baseurl, options, lock):
        self.plug = PlugD()
        self.baseurl = baseurl

    def handle(self, req, args):
        if not args or not args[0]:
            req.text_response(self.html())
            return

        target = args[0]
        if target == "icon":
            self.handle_icon(req, args[1:])
        elif target == "css":
            req.text_response(self.css(), encoding="css")
        elif target in ("on", "off", "toggle"):
            self.handle_command(req, args)
        else:
            req.send_error(404)

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
            output.write("<a class=\"plug_button\" href=\"toggle/%s\">" % (state.name))
            output.write("<img class=\"plug_icon\" src=\"icon/{0}\" alt=\"{0}\" /></a>".format(state.name))

    def add_environment(self, output):
        output.write(time.strftime("%H:%M ") + " ".join(hum_tem()))

    def css(self):
        css = os.path.expanduser("~/.plug/toggle_index.css")
        if os.path.exists(css):
            return open(css, 'r').read()
        else:
            return ""

    @needs_args(1)
    def handle_icon(self, req, args):
        target = args.pop(0)
        bare, flags = req.argsplit(args)

        encoding = "PNG" if not "encoding" in flags else flags["encoding"]
        icon = self.icon(urllib.unquote(target), encoding=encoding)
        if icon is None:
            req.send_error(404)
        else:
            req.image_response(icon, encoding=encoding)
            
    def icon(self, name, encoding="PNG"):
        states = self.plug.status()
        wanted = [state for state in states if state.name == name]
        if len(wanted) != 1:
            return None
        return PlugIcon(wanted[0]).to_binary(encoding=encoding)

    @needs_args(2)
    def handle_command(self, req, args):
        command, target = args[:2]
        target = urllib.unquote(target)
        success = self.command(command, target)
        if success:
            req.redirect_response("/%s/" % self.baseurl, text="success")
        else:
            req.send_error(404)

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
