# Environmental monitoring and control

This is the software component of a basic system I created for myself
to monitor and control the pre-season started seedlings I grow. It
runs on a Raspberry Pi Model B with a camera module and (currently)
two arduinos.

It has no non-standard requiremets in that environment outside of the
picamera module in terms of software, but it relies on some other
services being present (the python part lives in Servers/) which
provide a text over TCP interface to an underlying arduino system
(sketches live in Sketches/).

As it stands, this stuff "works for me". The reason I put it here is
to force myself to clean it up a bit.
