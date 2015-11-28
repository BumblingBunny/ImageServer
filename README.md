# Web interface for environmental monitoring

This is the web component of a basic system I created for myself to
monitor and control the pre-season started seedlings I grow (tomatoes,
beans, courgettes, peas, that kind of thing). It runs on a Raspberry
Pi Model B with a camera module.

It has no non-standard requiremets in that environment outside of the
picamera module in terms of software, but it relies on some other
services being present (lients for those are in PlugD.py and
Sensors.py) which provide a text over TCP interface to an underlying
arduino system. I'll post details and sketches for those separately.
