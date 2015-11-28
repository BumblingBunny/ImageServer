# Environmental monitoring and control

This is the web component of a basic system I created for myself to
monitor and control the pre-season started seedlings I grow. It runs
on a Raspberry Pi Model B with a camera module.

It has no non-standard requiremets in that environment outside of the
picamera module in terms of software, but it relies on some other
services being present (clients for those are in PlugD.py and
Sensors.py) which provide a text over TCP interface to an underlying
arduino system.

The setup I have comprises a custom-built arduino controlled "multi
plug", lights, a heater, a DHT11 sensor and other bits and bobs.

As it stands, this stuff "works for me". The reason I put it here is
to force myself to clean it up a bit. Expect rough edges, but please
do not hesitate to contact me on reddit (BumblingBunny) if you have
questions, suggestions, or other feed back.

The arduino sketches are in "/Sketches".

This project is in the public domain.
