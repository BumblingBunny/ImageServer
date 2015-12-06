# (Image)Server

Originally intended to just serve up pictures from the camera (hence
the ImageServer moniker) this has since grown a bit and now acts as an
image server, a web interface for the power box and simple file server
to serve MRTG data. It also serves up Humidity/Temperature (called
hum_tem throughout) data as plain text.

## Overview
[RequestHandler](ImageServer/RequestHandler.py) creates a few global
persistent objects (auth handler and generic handlers) when loaded,
then forwards requests to registered handlers. Which handler to call
is decided by the first element of the URL, e.g. if a request came
through (and passed auth) for "/bob/is/your/uncle", it will look for a
handler registered as "bob". That handler would then be called with a
request object and `["is", "your", "uncle"]` as arguments.

## Configuration
Everything the server relies on lives in ~/.plug/, including its main
config file: [web.conf](../dot-plug/web.conf), which contains one
mandatory section (`auth`), the optional but sensible `baseconfig`
section and any number of handler sections.

### `baseconfig`
Optional, but if not present the server will run single-threaded. You
can set `parallel` in here (supported options are `threading` and
`forking`) as well as override the default port to bind to by setting
`port`.

### A word about the module system
The `auth` and `handler` sections give directions on code to load via
two settings: `module` and, optionally, `location`. If `location` is
not present, it's set to the same as `module`. [Under the
hood](ImageServer/RequestHandler.py#L65), `location` is `import`ed,
then `module` is grabbed from the import and called with suitable
arguments. The result of this call must have a callable `handle`
attribute. Details on this are in the topic below.

### `auth`
Requires module config. The current implentation uses basic auth and
takes to extra lines in the config: `user` and `pwd`. The loaded
module is passed all options in this section as keyword args. The
`handle` is passed the request and must return `True` if
authentication succeeded. Any other result results in denied
access. In addition to the handle method, the authentication module
must implement an `auth_required_response` method. This, too, is
passed the request and should then send an appropriate response to the
client to request authentication.

The [current implementation](ImageServer/Authenticator.py) is pretty
straight forward, so it's probably easiest to look at it to understand
how it works.

### Handlers
Handlers require module config. Any section name that starts with
`handler:` is treated as a handler. Have a look at [the sample config
file](../dot-plug/web.conf) to get an idea of what a handler section
looks like. The bit of text after the colon specifies which subtree it
wants to manage (e.g. "bob", in the example above, would look like
this: `[handler:bob]`). The resulting module is instantiated by
passing it three keyword arguments: `baseurl` ("bob"), `options` (a
dict of the options in their section) and `lock`, a class suitable for
synchronisation given the chosen paralellism option.

There is a [BaseHandler](ImageServer/BaseHandler.py) class to inherit
from which currently does very little.

[SensorHandler](ImageServer/SensorHandler.py) is a very simple example
of what a handler could look like.
