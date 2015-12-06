# CameraHandler
And why you shouldn't name files before deciding on their purpose.

## CameraHandler.py
This handles all the web serving stuff, including routing requests to
sub-modules etc. The name derives from the fact that originally I was
just trying to serve up pictures from the Pi Camera. This is also why
the directory is still called ImageServer.

## Camera.py
This handles the actual camera interaction. It's almost general
purpose, but it annotates pictures it takes with results from PlugD.

## PlugDHandler.py
This encapsulates handling the web interface for the multiplug.

## PlugDImageAnnotator.py
Using base pictures from Camera.py, annotate them with details from
PlugD. Also provides PlubIcon class, providing images of plug states.

##PlugD.py and Sensors.py
Clients, see "/Servers" for details of the servers they talk to.
