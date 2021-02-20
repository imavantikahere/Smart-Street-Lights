from flask import Flask                     #importing Flask module
from flask import send_file                 #This is a flask function used to sent filesto the browser
import tuple                                #importing time module
from SmartLights import gettemp, gethumid   #import temperature and humidity functions from main code
myapp = Flask(__name__)                     #creating and flask app and naming it 'myapp'

import RPi.GPIO as GPIO                     #importing GPIO


light= 37
strongLight=38
flashlight=40

GPIO.setmode(GPIO.BOARD)                    #BOARD mode
GPIO.setup(light,GPIO.OUT)                  #setting the main light as output
GPIO.setup(stronglight,GPIO.OUT)            #setting the add on light as output
GPIO.setup(flashlight,GPIO.OUT)             #setting the flash/emergency light as output


password= 145                               #default password for admin use


@myapp.route('/')                           #default route
def index():                                # routing function index() attached to the route path (‘/’).
    temp=gettemp()                          #gets temperature from main code
    humidity= gethumid()                    #gets humidity from main code
    t=" Temp: %f "%temp                     #formatted temperature message
    h=" Humid: %f" %humidity                #formatted humidity message
    return "Welcome to the Smart Street Lights Panel. Time: "+time.ctime()+" "+ t+" C"+ h+" %"

@myapp.route("/showImage")                  #static route to display image of intruder/accessor
def myImage():                              #sends image captured by RPi to admin
    path = ('0.0.0.0:5020/showImage')       #this is where the Pi camera stores the image
    response=send_file('/home/pi/Desktop/photo.jpg',mimetype="image/jpeg") #image sent to browser
								    
    return response

@myapp.route("/showAccident")               #static route to display accident video
def myVideo():                              #sends accident scene captured by RPi to admin
    path = ('0.0.0.0:5020/showAccident')    #path at which RPi camera stores the video
    response=send_file('/home/pi/Desktop/video.jpg',mimetype="video/mp4")  #video sent to browser
								    
    return response

@myapp.route('/password/<code>')            #dynamic route to change password of manual access
def changePassword(code):                   #changes the password of the system to the code, allows 3 digits
    
    global password                         #password is a global variable since the change needs to reflect outside and beyond
    password= code
    return "Password changed successfully to "+ code

@myapp.route('/lights/<mainlight>/<addonLight>/<flash>') #dynamic route to control the lights
def controlLights(mainlight, addonLight, flash):         #mainlight, add on light and flash set by admin through url
    mainlight=int(mainlight)                             #cast to int        
    addonLight= int(addonLight)                          #cast to int
    flash= int(flash)                                    #cast to int
    message=""                                           #message to be displayed on browser
    if(mainlight==1):                                    #turns ON main light and displays message
        GPIO.output(light,1)
        message+="The main light is ON"
    else:                                                #turns OFF main light and displays message
        GPIO.output(mainlight,0)
        message+="The main light is OFF"
    message+= "<br>"
    if(addonLight==1):                                   #turns ON add on light and displays message
        GPIO.output(stronglight,1)
        message+=" The add on light is ON"
    else:                                                #turns OFF add on light and displays message
        GPIO.output(stronglight,0)
        message+=" The add on light is OFF"
    message+= "<br>"
    if(flash==1):                                       #turns ON flash light and displays message
        GPIO.output(flashlight,1)
        message+=" The flash light is ON"
    else:                                               #turns OFF flash light and displays message
        GPIO.output(flashlight,0)
        message+=" The flash light is OFF"
    return message
    
    

if __name__ == '__main__':  

    myapp.run(debug=True, host=‘0.0.0.0‘, port=5020)    
