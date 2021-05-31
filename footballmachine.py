from roboclaw_3 import Roboclaw
from time import sleep
import numpy as np
from threading import Thread
from optimizer import Optimizer

class Footballmachine:
    def __init__(self,address=[0x80,0x81],baudrate=38400,port="/dev/ttyS0"):
        self.address = address
        self.rc = Roboclaw(port, baudrate)
        self.rc.Open()
        self.M1speedconst=1.0
        self.M2speedconst=1.0
        self.optim=Optimizer()

    def has_angle_motor_stopped_moving(self):
        interval = 0.1
        first = self.rc.ReadEncM1(self.address[1])
        sleep(interval)
        second = self.rc.ReadEncM1(self.address[1])
        print(f"first: {first}, second: {second}")
        while(first!=second): 
            first = self.rc.ReadEncM1(self.address[1])
            sleep(interval)
            second = self.rc.ReadEncM1(self.address[1])

    def init_motors(self):
        for address in self.address:
            version = self.rc.ReadVersion(address)
            if version[0]==False:
                print(f"GETVERSION Failed - check power supply and conections on address {address}")
                #return
            else:
                print(repr(version[1]))

        print("Initializing all motors...")
        backward_speed = 126 #range: 0-126
        self.rc.BackwardM1(self.address[1],backward_speed)
        self.has_angle_motor_stopped_moving()
        self.rc.BackwardM1(self.address[1],0)
        self.rc.ResetEncoders(self.address[1])
        print("Angle encoder:", self.rc.ReadEncM1(self.address[1])[1])      
        
        
    def _speed_to_QPPS(self,speed,spin=0):
        angular_speed=speed/(0.1*2*np.pi)+spin*100
        QPPS=int(round(angular_speed*4000))
        return QPPS 

    def _QPPS_to_speed(self,QPPS):
        speed = QPPS/4000*(0.1*2*np.pi)
        return speed

    def _angle_to_QP(self,angle):
        range_min=0
        range_max=221
        angle_min=0
        angle_max=45
        a1=int(angle) - angle_min
        a2=range_max - range_min
        a3=angle_max - angle_min
        angle = int((a1 *a2)/a3 + range_min)
        return angle

    def check_speed(self,seconds):
        for i in range(0,seconds):
            print(("{} # ".format(i)), end=' ')
            enc1 = self.rc.ReadEncM1(self.address[0])
            enc2 = self.rc.ReadEncM2(self.address[0])
            speed1 = self.rc.ReadSpeedM1(self.address[0])
            speed2 = self.rc.ReadSpeedM2(self.address[0])

            print(("Encoder1:"), end=' ')
            if(enc1[0]==1):
                print(enc1[1], end=' ')
                print(format(enc1[2],'02x'), end=' ')
            else:
                print("failed", end=' ')
            print("Encoder2:", end=' ')
            if(enc2[0]==1):
                print(enc2[1], end=' ')
                print(format(enc2[2],'02x'), end=' ')
            else:
                print("failed ", end=' ')
            print("Speed1:", end=' ')
            if(speed1[0]):
                print(speed1[1], end=' ')
            else:
                print("failed", end=' ')
            print(("Speed2:"), end=' ')
            if(speed2[0]):
                print(speed2[1])
            else:
                print("failed ")
            sleep(0.1)
        
    def check_lowest_speeds(self,seconds):
        minspeedM1= np.Inf
        minspeedM2= np.Inf
        print("Wait two seconds before sending the ball. Film and measure landing position")
        sleep(2)
        for _ in range(0,seconds/10):
            speed1 = self.rc.ReadSpeedM1(self.address[0])
            speed2 = self.rc.ReadSpeedM2(self.address[0])
            if(speed1[0]):
                if speed1[1]<minspeedM1: minspeedM1= speed1[1]
            if(speed2[0]):
                if speed2[1]<minspeedM2: minspeedM2= speed2[1]
            sleep(0.1)
        return self._QPPS_to_speed(minspeedM1), self._QPPS_to_speed(minspeedM2)
    
    def calibrate_motor_constants(self,landingpoint,set_speed,set_angle,spin, tf,minspeedM1,minspeedM2):
        real_speed = self.optim.calculate_real_speed(landingpoint, set_speed, set_angle, spin, tf)
        self.M1speedconst=minspeedM1/real_speed
        self.M2speedconst=minspeedM2/real_speed
        return  self.M1speedconst, self.M2speedconst

    def manuell_shot(self,speed,angle,spin,dispenser_speed):
        print("Set_angle: ",angle)
        angle = self._angle_to_QP(angle)
        print("Target position M1:", angle)
        t0 = Thread(target=self.rc.SpeedAccelDeccelPositionM1,args=(self.address[1],10,10,10,angle,0))
        t0.start()
        t0.join()
        print("Angle encoder:", self.rc.ReadEncM1(self.address[1])[1])


        speedm2=int(self._speed_to_QPPS(speed,-spin)*self.M2speedconst)
        speedm1=int(self._speed_to_QPPS(speed,spin)*self.M1speedconst)
        self.rc.SpeedAccelM2(self.address[0],14000,int(speedm1))
        self.rc.SpeedAccelM1(self.address[0],14000,int(speedm2))
        self.rc.ForwardM2(self.address[1],dispenser_speed)


    def manuell_shot_done(self):
        self.rc.SpeedAccelM2(self.address[0],14000,0)
        self.rc.SpeedAccelM1(self.address[0],14000,0)
        self.rc.ForwardM2(self.address[1],0)

        t0 = Thread(target=self.rc.SpeedAccelDeccelPositionM1,args=(self.address[1],10,10,10,0,0))
        t0.start()
        t0.join()

    def landing_shot(self,target,dispenser_speed):
        speed,angle,spin,tf= self.optim.find_initvalues_spin(target)
        #self.optim.plot_path(speed,angle,spin)
        print(f"Optim values for {target} is {speed,angle,spin}")
        print("Set_angle: ",angle)
        angle = self._angle_to_QP(angle)
        print("Target position M1:", angle)
        #self.rc.SpeedAccelDeccelPositionM1(self.address[1],10,10,10,angle,0)
        t0 = Thread(target=self.rc.SpeedAccelDeccelPositionM1,args=(self.address[1],10,10,10,angle,0))
        t0.start()
        t0.join()
        print("Angle encoder:", self.rc.ReadEncM1(self.address[1])[1])
        sleep(7)
        #spin er gitt i radianer per sekund
        
        speed=self._speed_to_QPPS(int(speed))       
        speedM1=int((speed/(0.1*np.pi)-(spin/np.pi))*self.M2speedconst)
        speedM2=int((speed/(0.1*np.pi)+(spin/np.pi))*self.M1speedconst)


        self.rc.SpeedAccelM2(self.address[0],14000,speedM1)
        self.rc.SpeedAccelM1(self.address[0],14000,speedM2)
        self.rc.ForwardM2(self.address[1],dispenser_speed)
        return speed,angle,spin

    def test_spin(self,spin,speed):
        speedM1=self._speed_to_QPPS(speed,-spin)   
        speedM2=self._speed_to_QPPS(speed,spin)
         
        print(speedM1,speedM2)

fm = Footballmachine()
fm.test_spin(0.018,27)
