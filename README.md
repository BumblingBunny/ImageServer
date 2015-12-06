# Environmental monitoring and control

This is the software component of a basic system I created for myself
to monitor and control the pre-season started seedlings I grow. It
runs on a Raspberry Pi Model B with a camera module and (currently)
two arduino (compatible) things.

As it stands, this stuff "works for me". The reason I put it here is
to force myself to clean it up a bit.

## Server
This contains a python BaseHTTPServer based web server providing
access to the camera as well as the arduino frontends via a simple web
interface. It is configured via [web.conf](dot-plug/web.conf). To use
it, simply run [tree.py](server/tree.py). By default, it will bind to
port 8008, enforce Basic Auth and then return nothing but 404s, it
needs handlers to be specified in the web.conf to be useful.

## dot-plug
Bits of configuration, templates and pictures. Most of these are for
the web server component, but any other config goes in here as well.

## ArduinoFrontends
Both the arduinos are used by multiple systems outside of the web
frontend, so there needed to be a layer between them and those
clients to avoid serial contention. They're pretty basic.

## Sketches
Speaking of arduino, the sketches for them are here.

## mrtg
My mrtg config and the client script for the sensor which feeds mrtg.
