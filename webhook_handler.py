#!/usr/bin/env python
#-*- coding:utf-8 -*-

import BaseHTTPServer
import sys
import time
import urlparse
import json

import RPi.GPIO as GPIO
import time

#colors = [0xFF00, 0x00FF, 0x0FF0, 0xF00F]
Green = 0x00FF
Red = 0xFF00
Off = 0x0000
pins = {'pin_R':11, 'pin_G':12}  # pins is a dict

GPIO.setmode(GPIO.BOARD)       # Numbers GPIOs by physical location
for i in pins:
    GPIO.setup(pins[i], GPIO.OUT)   # Set pins' mode is output
    #GPIO.output(pins[i], GPIO.HIGH) # Set pins to high(+3.3V) to off led

p_R = GPIO.PWM(pins['pin_R'], 2000)  # set Frequece to 2KHz
p_G = GPIO.PWM(pins['pin_G'], 2000)

p_R.start(0)      # Initial duty Cycle = 0(leds off)
p_G.start(0)

def map(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def setColor(col):   # For example : col = 0x112233
    R_val = (col & 0x1100) >> 8
    G_val = (col & 0x0011) >> 0

    R_val = map(R_val, 0, 255, 0, 100)
    G_val = map(G_val, 0, 255, 0, 100)
	
    p_R.ChangeDutyCycle(R_val)     # Change duty cycle
    p_G.ChangeDutyCycle(G_val)

def loop():
    while True:
        setColor(Red)
        time.sleep(1)
        setColor(Green)
        time.sleep(1)

def destroy():
    p_R.stop()
    p_G.stop()
    for i in pins:
        GPIO.output(pins[i], GPIO.HIGH)    # Turn off all leds
    GPIO.cleanup()

HOST_NAME = sys.argv[1]
PORT_NUMBER = int(sys.argv[2])


def handle_hook(payload):
    pass


class HookHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    server_version = "HookHandler/0.1"
    def do_GET(s):
        s.send_response(200)
        s.wfile.write('Hello!')

    def do_POST(s):
        # Check that the IP is within the GH ranges
        if not any(s.client_address[0].startswith(IP)
                   for IP in ('192.30.252', '192.30.253', '192.30.254', '192.30.255')):
            s.send_error(403)

        length = int(s.headers['Content-Length'])
        post_data = urlparse.parse_qs(s.rfile.read(length).decode('utf-8'))
        # payload = json.loads(post_data['payload'][0])
        # handle_hook(payload)
        setColor(Green)
        time.sleep(5)
        setColor(Off)
		
        s.send_response(200)


if __name__ == '__main__':
    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), HookHandler)
    print time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER)
