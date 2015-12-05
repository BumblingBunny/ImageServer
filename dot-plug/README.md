# Pre-made images and such

These need to live in ~/.plug/ on the pi.

## web.conf
Contains config for the python web server, including which modules to
load.

## plugd.conf
Aliases for the plugs. The arduino sketch only accepts numerical
"slot" numbers, each line in this file adds an alias for those
slots. You will have to create a PNG picture for the names chosen
(e.g. if you name a slot "Fred Fredson", the image needs to be called
"Fred Fredson.png") to make the graphical side of this work.

## toggle_index.*
The .html that gets served up for web control with very basic
templating to fill in buttons for the multi plug
temperature/humidity. I run MRTG to graph the latter, so that's
included in the html as well. The css is just served as is.

## Blank.png, Off.png
These are "special". A slot called "Blank .*" in the plugd.conf gets
the "Blank.png" icon (they still need to be numbered, e.g. "Blank 1"
if you ever want to interact with them). My multi-plug uses C14
sockets, hence the picture.

Off.png gets pasted on top of slot icons if they are currently powered
off. It can be omitted, in which case a red cross is drawn across the
image instead.


