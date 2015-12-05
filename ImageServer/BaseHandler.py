def needs_args(count):
    def enforce_args(func):
        def wrapped(self, req, args):
            if len(args) < count:
                req.send_error(404)
                return
            elif len([x for x in args[:count] if len(x) > 0]) < count:
                req.send_error(404)
                return
            result = func(self, req, args)
            return result
        return wrapped
    return enforce_args


class BaseHandler(object):
    def __init__(self, baseurl, options, lock):
        pass

    def handle(self, req, args):
        req.send_error(404)
