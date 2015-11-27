"""
Module to talk to plugd
"""

import socket
import os

SLOT_NAMES = [
    "Broken",
    "Warm Light",
    "Daylight Light",
    "Heater",
    "Main Light",
    "Extractor"
]

G_PLUGD = None

class PlugStatus(object):
    def __init__(self, status_line):
        self.pos = int(status_line[1])
        self.state = status_line.split()[-1]
        self.on = self.state == "LOW"
        self.name = SLOT_NAMES[self.pos]

def PlugD(host="localhost", port=3019):
    """
    To things to note:
    * Yes, this is thread safe. Creating the global object a few times
      does no harm, this is just to aboud doing it over and over again.
    * Yes, as it is currently that means only one plugd can be spoken
      to, every subsequent attempt to instantiate one yields whichever
      config G_PLUGD happened to get
    """
    global G_PLUGD
    if G_PLUGD is None:
        G_PLUGD = _PlugD(host, port)
    return G_PLUGD

class _PlugD(object):
    def __init__(self, host="localhost", port=3019):
        self.host = host
        self.port = port

        slot_source = [x for x in ("/etc/plugd.conf", os.path.expanduser("~/.plug/plugd.conf")) if os.path.exists(x)]
        if len(slot_source) > 0:
            global SLOT_NAMES
            SLOT_NAMES = open(slot_source[0]).read().splitlines()

    def lights_on(self):
        "Returns true if any of the lights are on, False otherwise"
        status = self.status()
        for st in status:
            if "Light" in st.name and st.on:
                return True
        return False

    def send_command(self, command):
        "Send raw plugd commands"
        plugd = socket.create_connection(("localhost", self.port), 2)
        plugd.send(command)
        data = plugd.recv(512)
        plugd.close()
        return self._get_status(data)

    def _get_status(self, data):
        data = data.splitlines()
        return [PlugStatus(line) for line in data if line.startswith("#")]

    def status(self):
        "Returns current plug status"
        return self.send_command("ss")

    def _resolve_slot(self, slot):
        if isinstance(slot, int):
            if slot < 0 or slot > len(SLOT_NAMES):
                raise ValueError("Invalid slot number")
            return slot
        elif not isinstance(slot, basestring):
            raise ValueError("Invalid slot type")
        elif slot in SLOT_NAMES:
            return SLOT_NAMES.index(slot)
        else:
            for i, s in enumerate(SLOT_NAMES):
                if s.startswith(slot):
                    return i
        raise ValueError("Failed to resolve slot")

    def _switch(self, slot, enable):
        try:
            pos = self._resolve_slot(slot)
        except:
            return None
        if enable:
            return self.send_command("e"+str(pos))
        else:
            return self.send_command("d"+str(pos))

    def enable(self, slot):
        "Enables the slot (by name or number)"
        return self._switch(slot, True)

    def disable(self, slot):
        "Disables the slot (by name or number)"
        return self._switch(slot, False)

    def toggle(self, slot):
        "Toggles the slot (by name or number)"
        try:
            return self.send_command("t" + str(self._resolve_slot(slot)))
        except:
            return None
