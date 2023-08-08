import RPi.GPIO as GPIO
import time
#color sensor pins
s2 = 19 # Raspberry Pi Pin 35
s3 = 13 # Raspberry Pi Pin 33
out = 26 # Pin 37

motionStatus="F" # F for forward, R for right, L for left

#steering motor pins
g1 = 23
g2 = 24

#drive motor pins
g3=18
g4 = 12

#start button
b = 27

# distance sensors pins
#left
TRIG_l=7
ECHO_l=1
#right 
TRIG_r=25
ECHO_r=8
#head
TRIG_h=20
ECHO_h=21

#corner lines counter
counter=0

NUM_CYCLES = 10

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(out,GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(s2,GPIO.OUT)
    GPIO.setup(s3,GPIO.OUT)
    GPIO.setup(b, GPIO.IN)
    GPIO.setup(g1, GPIO.OUT)
    GPIO.setup(g2, GPIO.OUT)
    GPIO.setup(g3, GPIO.OUT)
    GPIO.setup(g4, GPIO.OUT)
    GPIO.setup(TRIG_l,GPIO.OUT)
    GPIO.setup(ECHO_l,GPIO.IN)
    GPIO.setup(TRIG_r,GPIO.OUT)
    GPIO.setup(ECHO_r,GPIO.IN)
    GPIO.setup(TRIG_h,GPIO.OUT)
    GPIO.setup(ECHO_h,GPIO.IN)
    GPIO.setwarnings(False)

def steerMotor(direction):
    if direction==2: #left
        GPIO.output(g1, GPIO.LOW)
        GPIO.output(g2, GPIO.HIGH)
    if direction==1: #right
        GPIO.output(g1, GPIO.HIGH)
        GPIO.output(g2, GPIO.LOW) 
    if direction==0: #head
        GPIO.output(g1, GPIO.LOW)
        GPIO.output(g2, GPIO.LOW)

def read_value(a0, a1):
    
    GPIO.output(s2, a0)
    GPIO.output(s3, a1)
    time.sleep(0.1)
    GPIO.wait_for_edge(out, GPIO.FALLING)
    GPIO.wait_for_edge(out, GPIO.RISING)
    start = time.time()
    GPIO.wait_for_edge(out, GPIO.FALLING)
    return (time.time() - start) * 1000000

def stopMotor():
    GPIO.output(g3, GPIO.LOW)
    GPIO.output(g4, GPIO.LOW)
    GPIO.output(g1, GPIO.LOW)
    GPIO.output(g2, GPIO.LOW)

def getDistance(trig, echo):
        
    GPIO.output(trig, False)                 #Set TRIG as LOW
    time.sleep(0.00000000000001)                            #Delay of 2 seconds
    GPIO.output(trig, True)                  #Set TRIG as HIGH
    time.sleep(0.00000000000001)                   
    GPIO.output(trig, False)                 #Set TRIG as LOW
    while GPIO.input(echo)==0:               #Check whether the ECHO is LOW
        pulse_start = time.time()              #Saves the last known time of LOW pulse
    while GPIO.input(echo)==1:               #Check whether the ECHO is HIGH
        pulse_end = time.time()                #Saves the last known time of HIGH pulse 
    pulse_duration = pulse_end - pulse_start #Get pulse duration to a variable
    distance_r = pulse_duration * 17150        #Multiply pulse duration by 17150 to get distance
    distance_r = round(distance_r, 2)            #Round to two decimal points
    return distance_r

def adjust():
    GPIO.output(g1, GPIO.LOW)
    GPIO.output(g2, GPIO.HIGH)
    time.sleep(0.2)
    GPIO.output(g1, GPIO.HIGH)
    GPIO.output(g2, GPIO.LOW)
    time.sleep(0.2)
    GPIO.output(g1, GPIO.LOW)
    GPIO.output(g2, GPIO.HIGH)
    time.sleep(0.08)
    GPIO.output(g1, GPIO.LOW)
    GPIO.output(g2, GPIO.LOW)

    #ultra_left
def driveForward():
    time.sleep(0.22)
    GPIO.output(g3, GPIO.HIGH)
    GPIO.output(g4, GPIO.LOW)
    time.sleep(0.22)

def getColor():
    color="w"
    r= read_value(GPIO.LOW, GPIO.LOW)
    g = read_value(GPIO.HIGH, GPIO.HIGH)
    b = read_value(GPIO.LOW, GPIO.HIGH)
    if(r<400) and (g<400) and (b<400):
        color="w"
    elif(r<b) and (r<g):
        color="o"
    elif(b<r) and (b<g):
        color="b"
    return color

def loop():
    start=0
    end=0
    go=0
    finish=False
    counter=0
    while(True):    
        #wait for press go
        if GPIO.input(27) == GPIO.LOW and go == 0:
            time.sleep(0.18)
            
            print("Go!!!")

            steerMotor(0)
            stopMotor()
            adjust()
            
            go = 1
            # Drive straight
            driveForward()
         
            while(True):
                if GPIO.input(27) == GPIO.LOW and go == 1:
                    go=2
                    time.sleep(0.18)
                    stopMotor()
                    break
                
                #read color sensor
                
                color=getColor()
                if (color=="b") or (color=="o"):
                    counter+=1
                    if(counter==1):
                        while(True):
                            r = getDistance(TRIG_r,ECHO_r)
                            l = getDistance(TRIG_l,ECHO_l)
                            h = getDistance(TRIG_h,ECHO_h)
                            if(h<40):
                                stopMotor()
                            elif(r>150):
                                motionStatus="R"
                                #steer right
                                break
                            elif (l>150):
                                motionStatus="L"
                                #steer Left
                                break
                    if(counter%2!=0):
                        start=time.time()
                        if(motionStatus=="R"):
                            time.sleep(1)
                            steerMotor(1)
                        elif(motionStatus=="L"):
                            time.sleep(1)
                            steerMotor(2)
                    elif(counter%2==0):
                        end=time.time()
                        t=end-start
                        time.sleep(t)
                        stopMotor()
                        steerMotor(0)
                        adjust()
                        time.sleep(5)
                        driveForward()
                        
                elif color=="w" and counter%2==0:
                    # camera code here
                    
                    r = getDistance(TRIG_r,ECHO_r)
                    l = getDistance(TRIG_l,ECHO_l)
                    h = getDistance(TRIG_h,ECHO_h)
                    if(h<40):
                        stopMotor()
                    elif r<25:
                        while True:
                            r = getDistance(TRIG_r,ECHO_r)
                            l = getDistance(TRIG_l,ECHO_l)
                            h = getDistance(TRIG_h,ECHO_h)
                            if(h<100) or (r>25):
                                #stopMotor()
                                steerMotor(0)
                                adjust()
                                #driveForward()
                                break
                            if r<25:
                                steerMotor(2)
                    elif l<25:
                        while True:
                            r = getDistance(TRIG_r,ECHO_r)
                            l = getDistance(TRIG_l,ECHO_l)
                            h = getDistance(TRIG_h,ECHO_h)
                            if(h<100) or (l>25):
                                #stopMotor()
                                steerMotor(0)
                                adjust()
                                #driveForward()
                                break
                            if l<25:
                                steerMotor(1)
                                  
                   
                if(counter==24):
                    finish=True
                    time.sleep(5)
                    steerMotor(0)
                    stopMotor()
                    adjust() 
                    break
                
        if go == 2 or finish==True:
            print("Finished!!!")
            stopMotor()
            break
                 
                

if __name__=='__main__':
    setup()

    try:
        loop()
    except:
        print("Something wrong")
        stopMotor()
        GPIO.cleanup()
 