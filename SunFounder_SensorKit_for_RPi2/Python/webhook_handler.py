#!/usr/bin/env python
import BaseHTTPServer
import sys
import time
import urlparse
import json
import cgi
import pprint

import RPi.GPIO as GPIO
import time

import LCD1602
import time

GPIO.setwarnings(False)

def lcd_disp(line1, line2):
    LCD1602.init(0x27, 1)   # init(slave address, background light)
    LCD1602.write(0, 0, line1)
    LCD1602.write(1, 1, line2)
    time.sleep(2)

def loop():
    space = '                '
    greetings = 'Thank you for buying SunFounder Sensor Kit for Raspberry! ^_^'
    greetings = space + greetings
    while True:
        tmp = greetings
        for i in range(0, len(greetings)):
            LCD1602.write(0, 0, tmp)
            tmp = tmp[1:]
            time.sleep(0.8)
            LCD1602.clear()

def destroy():
    pass

# Green = 0x00FF
# Red = 0xFF00
# Off = 0x0000
# pins = {'pin_R':11, 'pin_G':12}  # pins is a dict

# GPIO.setmode(GPIO.BOARD)       # Numbers GPIOs by physical location
# for i in pins:
#     GPIO.setup(pins[i], GPIO.OUT)   # Set pins' mode is output
#     #GPIO.output(pins[i], GPIO.HIGH) # Set pins to high(+3.3V) to off led

# p_R = GPIO.PWM(pins['pin_R'], 2000)  # set Frequece to 2KHz
# p_G = GPIO.PWM(pins['pin_G'], 2000)

# p_R.start(0)      # Initial duty Cycle = 0(leds off)
# p_G.start(0)

# def map(x, in_min, in_max, out_min, out_max):
#     return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

# def setColor(col):   # For example : col = 0x112233
#     R_val = (col & 0x1100) >> 8
#     G_val = (col & 0x0011) >> 0

#     R_val = map(R_val, 0, 255, 0, 100)
#     G_val = map(G_val, 0, 255, 0, 100)

#     p_R.ChangeDutyCycle(R_val)     # Change duty cycle
#     p_G.ChangeDutyCycle(G_val)

# def loop():
#     while True:
#         setColor(Red)
#         time.sleep(1)
#         setColor(Green)
#         time.sleep(1)

# def destroyLED():
#     p_R.stop()
#     p_G.stop()
#     for i in pins:
#         GPIO.output(pins[i], GPIO.HIGH)    # Turn off all leds
#     GPIO.cleanup()

HOST_NAME = sys.argv[1]
PORT_NUMBER = int(sys.argv[2])

BuzzerPin = 11
GPIO.setmode(GPIO.BOARD)
GPIO.setup(BuzzerPin, GPIO.OUT)
GPIO.setup(BuzzerPin, GPIO.HIGH)

def on():
    GPIO.output(BuzzerPin, GPIO.LOW)

def off():
    GPIO.output(BuzzerPin, GPIO.HIGH)

def beep(x):
    on()
    time.sleep(x)
    off()
    time.sleep(x)

def loop(t):
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(BuzzerPin, GPIO.OUT)
    start = time.time()
    while time.time() - start <= t:
        beep(0.5)
    destoryBuzzer()

def destoryBuzzer():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(BuzzerPin, GPIO.OUT)
    GPIO.output(BuzzerPin, GPIO.HIGH)
    GPIO.cleanup()

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
                   for IP in ('192.30.252',
                              '192.30.253',
                              '192.30.254',
                              '192.30.255')):
            print("Unknown source: {}".format(s.client_address[0]))
            s.send_error(403)

        ctype, pdict = cgi.parse_header(s.headers['content-type'])
	#print(ctype)
	#print(pdict)
        length = int(s.headers['content-length'])
	#print(length)
        post_data = json.loads(s.rfile.read(length))
        # pprint.pprint(post_data)
        #print(type(post_data))

        if 'pusher' in post_data:
            line1 = post_data['pusher']['name']
        else:
            line1 = "Greetings"
        if 'repository' in post_data:
            line2 = post_data['repository']['name']
        else:
            line2 = "from Kepler!"

        lcd_disp(line1, line2)

	#for key in post_data:
	#	print(key)

	# payload = json.loads(post_data['payload'][0])
        # handle_hook(payload)
        # setColor(Green)

        loop(3)
        # time.sleep(5)
        # setColor(Off)

        s.send_response(200)


if __name__ == '__main__':
    # setup(Buzzer)
    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), HookHandler)
    print time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    destoryBuzzer()
    print time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER)
