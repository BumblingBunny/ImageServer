from BaseHandler import BaseHandler
from Sensors import hum_tem

class SensorHandler(BaseHandler):
    def handle(self, req, args):
        try:
            hum, tem = hum_tem()
        except:
            req.send_error(500)
            return
        req.text_response("RH: %s\r\nT : %s\r\n" % (hum, tem), encoding="plain")

    
