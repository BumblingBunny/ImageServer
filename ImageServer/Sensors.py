import socket

def hum_tem(host="localhost", port=3020):
    hum = "NaN %"
    tem = "NaN C"
    sensor = socket.create_connection((host, port), 2)
    sensor.send("humidity")
    hum = sensor.recv(512)
    sensor = socket.create_connection((host, port), 2)
    sensor.send("temperature")
    tem = sensor.recv(512)

    return hum+"%", tem+"C"
