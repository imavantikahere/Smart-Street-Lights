import PCF8591 as ADC                   #import PCF8591 library
import time                             #import time library
import datetime                         
import serial                           
import LCD1602 as LCD                   #import LCD module
fom flask import Flask                  #importing Flask module to Python script
from picamera import PiCamera           #from picamera import PiCamera
from web import password                #password imported from flask code, since it
                                        #is set and changed remotely
LCD.init(0x27, 1)                       #initialize LCD with slave address and backgroundlight
ADC.setup (0x48)                        #setup I2C address


SERIAL_PORT= '/dev/ttys0'               #serial port address
#setting up serial port as per the Parallax reader datasheet
ser= serial.Serial(baudrate= 2400,
                   bytesize= serial.EIGHTBITS
                   parity= serial.PARITY_NONE
                   port= SERIAL_PORT
                   stopbits= serial.STOPBITS_ONE
                   timeout=1)

light= 37                               #this is the mainlight being used set as output
GPIO.setmode(GPIO.BOARD)
GPIO.setup(light, GPIO.OUT)

stronglight=38                          #this is the additional light that is turned ON in  case of fog

interruptswitch=22                      #Used as the interrupt signal
GPIO.setup(interruptswitch, GPIO.IN, pull_up_down= GPIO.PUD_DOWN)

flashlight= 40                          #emergency flashing lights
GPIO.setup(flashlight, GPIO.OUT)        #emergency flashlight set as LED output

RFIDEnable= 24                          #Enable output pin for RFID
GPIO.setup(RFIDEnable, GPIO.OUT)

manualswitchlight= 25                   #Switch to directly switch ON/OFF the normal light
manualswitchadd= 26                     #Switch to directly switch ON/OFF the additional light
manualswitchflash= 27                   #Switch to directly switch ON/OFF the addition light
manualindicator= 8                      #This output is connected to a DC light source to indicate that the
                                        #user has successfully entered manual mode

GPIO.setup(manualswitchlight, GPIO.IN)
GPIO.setup(manualswitchadd, GPIO.IN)
GPIO.setup(manualswitchflash, GPIO.IN)
GPIO.setup(manualindicator, GPIO.OUT)

TRIG = 19                               #Trigger output for ultrasonic sensor
ECHO = 20                               #Echo input forthe ultrasonic sensor
Buzzer=16                               #PWM output for Buzzer
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
GPIO.setup(Buzzer, GPIO.OUT)

Mycamera= PiCamera()                     #creating an instance of PiCamera class

# 3 x 3 keypad rows and columns
#setting up pins as input and pullup resistors for rows
GPIO.setup(1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#setting up pins as outputs
GPIO.setup(4, GPIO.OUT)
GPIO.setup(5, GPIO.OUT)
GPIO.setup(6, GPIO.OUT)
def keypad():  #function for keypad
    while(True): 

        #Column-1 Pin 11 low
        GPIO.output(4, GPIO.LOW)
        GPIO.output(5, GPIO.HIGH)
        GPIO.output(6, GPIO.HIGH)

        #Scanning row 1
        if (GPIO.input(1)==0):
            return(1)
            break
        #Scanning row 2
        if (GPIO.input(2)==0):
            return(4)
            break
        #Scanning row 3
        if (GPIO.input(3)==0):
            return(7)
            break

         #Column 2 Pin 13 low
        GPIO.output(4, GPIO.HIGH)
        GPIO.output(5, GPIO.LOW)
        GPIO.output(6, GPIO.HIGH)

          #Scanning row 1
        if (GPIO.input(1)==0):
            return(2)
            break
        #Scanning row 2
        if (GPIO.input(2)==0):
            return(5)
            break
        #Scanning row 3
        if (GPIO.input(3)==0):
            return(8)
            break

         # column 3 Pin 15 low

        GPIO.output(4, GPIO.HIGH)
        GPIO.output(5, GPIO.HIGH)
        GPIO.output(6, GPIO.LOW)

          #Scanning row 1
        if (GPIO.input(1)==0):
            return(3)
            break
        #Scanning row 2
        if (GPIO.input(2)==0):
            return(6)
            break
        #Scanning row 3
        if (GPIO.input(3)==0):
            return(9)
            break
        
def gettemp():

    Temp_units= ADC.read(1)/0.7         #read ADC units of channel 1, where temperature sensor is connected
                                        #dividing by gain because of inverting amplifier SCC
    Temp_volts= (Temp_units *3.3)/256   #Convert ADC units to Volts
    Temp_C= Temp_volts/0.01             #convert voltage to C
    return Temp_C

def gethumid():
    
    Hum_units= ADC.read(2)/2            #read ADC units of channel 2, where humidity sensor is connected
                                        #dividing by gain because of non inverting amplifier SCC
    Hum_volts= (Hum_units *3.3)/256     #Convert ADC units to Volts
    Hum_RH= (Hum_volts-0.985)/0.01307   #convert voltage to humidity
    return Hum_RH
    
def LIGHT_ON():                         #function to switch light on
    GPIO.output(light, GPIO.HIGH)

def LIGHT_OFF():                        #function to switch light off
    GPIO.output(light, GPIO.LOW)

def FlashLights():                     #Function flash emergency Light
    GPIO.output(GPIO.HIGH)
    time.sleep(1)
    GPIO.output(GPIO.LOW)
    time.sleep(1)

def LCDDisplay(temp, humid):
    
    time= time.ctime()                  #gets the time in day month hh:mm:ss year format
    time= time[:16]                     #strips the time to fit the LCD 
    temp_msg= "%d C"%int(temp)          #this is the temperature message to be printed on the LCD, eg 25 C,
                                        #cast to int to fit LCD
    humid_msg= " %d%"%int (humid)       #this is the humidity message tobe printed on the LCD, eg 71 %, cast
                                        #to int to fit LCD
    total_message= temp_msg + humid_msg #message on first line--> temp and humidty, eg 25 C 71%
    LCD.write(0,0, total_message)       #message displayed on first line of LCD
    LCD.write(0,1,time)                 #time displayed on second line of LCD
    LCD.sleep(1)
    
def lowlight( temp,  humid):            #The lowlight() function checks if the temperature and humidty are 
                                        # low andd high enough to cause low visibility
    now = datetime.datetime.now().time()#gets the time
    if (temp < 15 and humid > 50):      #We have considered temperature below 15 degrees and humidity above 
                                        #50 degrees as low visibility
        LIGHT_ON()                      #Light goes ON if temperature is below 10 and humidity is above 50
    #checking for time
    elif (now.hour >= 16 and (now.hour<=23 and now.minute <=59))
        LIGHT_ON()
    elif(now.hour>=0 and now.hour<5)
        LIGHT_ON()
    else:
        LIGHT_OFF()

def Verylowlight(temp, humid):          #The Verylowlight() function checksif there is fog, which is formed below 
                                        #5 degrees and humidty > 70
    if (temp <5 and humid >70):         #If temperature below 5 and humidty above 70, additional light switches ON
        GPIO.output(strongLight,GPIO.HIGH) 
        FlashLights()                   #Flash emergency lights continuously
        
                                       
    else:
        GPIO.output(strongLight, GPIO.LOW)  #else, no need of the additional or flash lights
        GPIO.output(flashlight, GPIO.LOW) 

def validate_rfid(code):
    s= code.decode("ascii")             #code convertedto ASCII
    if((len(s) == 12) and (s[0] == "\n") and (s[11] =="\r")):
        return s[1:-1]                  #Code is correct and hence the line feed and carriage return are stripped and returned
    else:
        return False

#calculate distance from two signals
def readdistance():
  

  GPIO.output(TRIG, GPIO.LOW)           #TRIGGER SET TO LOW
  time.sleep(0.000002)                  #SLEEP for 2 us
  GPIO.output(TRIG, 1)                  #TRIGGER SET TO HIGH
  time.sleep(0.00001)                   #HIGH FOR 10US
  GPIO.output(TRIG, 0)                  #TRIGGER SET TO LOW
  
  while GPIO.input(ECHO)==0:            #if echo is 0, nothing happens
    a=0                                 #dummy variable
  t1=time.time()
  while GPIO.input(ECHO)==1:            #time interval measured for ECHO high time
    a=0
  t2=time.time()
  totalTime=t2-t1                       #getting the time interval
  
  distance = totalTime *1000000/58      #getting the distance from the time interval
  return distance

def ultrasonic():
  distance=readdistance()/100

 #set up buzzer to pulse width modulator (for square wave)
 buzzer = GPIO.PWM(Buzzer, 500)
    #if distance less than 1 cm
 if(distance<2):
        buzzer.start(50)#start with duty cycle 50%
        Mycamera.start_preview()#start camera preview
        time.sleep(2)#sleep for 2 s
        Mycamera.start_recording(video_path) #start recording
        time.sleep(5) # capture the vieo for 5 seconds
        Mycamera.stop_recording() #stop recording                                                       
        Mycamera.close()  #close camera
        buzzer.stop()#stop the buzzer

def Authenticate(self):
    data= ser.read(12)                  #Reading 12 bytes from serial port
    code= validate_rfid(data)           #Validate the rfid code
    if code:
        if (code ==3456777778):         #This is our RFID code
            GPIO.output(manualindicator, GPIO.HIGH)
            GPIO.output(light, GPIO.input(manualswitchlight))
            GPIO.output(flashlight, GPIO.input(manualswitchlflash))
            GPIO.output(stronglight, GPIO.input(manualswitchadd))
            
    else:
        key1= keypad()                  #gets first key input
        time.sleep(0.5)                 #half second delay
        key2= keypad()                  #gets second key input
        time.sleep(0.5)                 #half second delay
        key3= keypad()                  #gets third key input
        time.sleep(0.5)                 #half second delay
        key= str(key1) + str(key2) + str(key3) #combines the keys
        if(key==password):              #checks if key equals password,if so, all lights are turned
                                        #On/Off depending on manual switches
            GPIO.output(manualindicator, GPIO.HIGH) #manual indicator turned ON, meaning successful access
            GPIO.output(light, GPIO.input(manualswitchlight))
            GPIO.output(flashlight, GPIO.input(manualswitchlflash))
            GPIO.output(stronglight, GPIO.input(manualswitchadd))
        else:                           #else picture of intruder is taken and saved. Later sent to admin via Flask
            camera.start_preview()      #camera preview starts
            time.sleep(2)               #2 second delay for stablization
            camera.capture('/home/pi/Desktop/photo.jpg') #saved image in given path
            camera.stop_preview()       #stops preview
            camera.close()              #closes camera
    GPIO.output(manualindicator, GPIO.LOW) #manual indicator turned ON
    

    
#This keeps checking the edge of the interruptswitch, if rising, then verylowlight ISR executed        
GPIO.add_event(interruptswitch, GPIO.BOTH, callback= Authenticate, bouncetime= 2000)    
while True:
    temp =gettemp()
    humid=gethumid()
    LCDDisplay(temo, humid)             #Carries out LCD displays of time, temperature and humidity
    lowlight(temp, humid)               #if temperature is below 10 degrees and humidity above 50 OR
                                        #if it is night time, lights turned on
    Verylowlight(temp, humid)           #if temperature is below 5 degrees and humidty above 70 (fog),
                                        #additional lights ON
    ultrasonic()                        #checks distance and buzzer is ON in case of an accident for the
                                        #duration of time that picture of scene if captured
    
    

    
    
    

    
    
    
    

    

    
    


    
