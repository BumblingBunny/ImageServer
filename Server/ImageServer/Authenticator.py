import base64

class Authenticator(object):
    def __init__(self, user=None, pwd=None, **kwargs):
        if user is None or pwd is None:
            raise Exception("Auth config (user/pwd) required!")
        self.basic_header = "Basic " + base64.encodestring("%s:%s" % (user, pwd)).strip()

    def handle(self, req):
        if req.headers.getheader('Authorization') is None:
            return False
        elif req.headers.getheader('Authorization') == self.basic_header:
            return True
        return False

    def auth_required_response(self, req):
        req.send_response(401)
        req.send_header('WWW-Authenticate', 'Basic realm=\"Mon\"')
        req.content_type('text/plain')
        req.start_response()
        req.wfile.write("GNU Terry Pratchet")
