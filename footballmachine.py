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
        self.spin_constant = 1.0
        self.M1speedconst=1.0
        self.M2speedconst=1.0
        self.optim=Optimizer()

    def has_angle_motor_stopped_moving(self):
        interval = 0.1
        first = self.rc.ReadEncM1(self.address[1])[1]
        sleep(interval)
        second = self.rc.ReadEncM1(self.address[1])[1]
        print(f"first: {first}, second: {second}")
        if first == second: return True
        else:
            while(first!=second): 
                first = self.rc.ReadEncM1(self.address[1])[1]
                sleep(interval)
                second = self.rc.ReadEncM1(self.address[1])[1]
            return True

    def init_motors(self):
        for address in self.address:
            version = self.rc.ReadVersion(address)
            if version[0]==False:
                print(f"GETVERSION Failed - check power supply and conections on address {address}")
            else:
                print(repr(version[1]))

        print("Initializing all motors...")
        self.rc.SpeedAccelM2(self.address[0],84000,0)
        self.rc.SpeedAccelM1(self.address[0],84000,0)
        self.rc.ForwardM2(self.address[1],0)
        backward_speed = 126 #range: 0-126
        self.rc.BackwardM1(self.address[1],backward_speed)
        self.has_angle_motor_stopped_moving()
        self.rc.BackwardM1(self.address[1],0)
        self.rc.ResetEncoders(self.address[1])
        
        print("Angle encoder:", self.rc.ReadEncM1(self.address[1])[1])      
        
        
    def _speed_to_QPPS(self,speed,spin=0):
        radius = 0.1
        encoder_pulses_per_rad = 1024*(180/3.14)/360
        angular_speed1=speed/radius*3.95*1.0-spin*1000*1.0
        angular_speed2=speed/radius*3.95*1.0+spin*1000*1.0
        print(angular_speed1,angular_speed2)
        QPPS1= encoder_pulses_per_rad*angular_speed1
        QPPS2= encoder_pulses_per_rad*angular_speed2
        print(QPPS1,QPPS2)
        if QPPS1>184879: QPPS1=184879
        if QPPS2>178401: QPPS2=178401
        return round(QPPS1), round(QPPS2)

    def _QPPS_to_speed(self,QPPS1,QPPS2):
        speed1 = QPPS1/(4000*self.M1speedconst)*(0.1*2*np.pi)
        speed2 = QPPS2/(4000*self.M2speedconst)*(0.1*2*np.pi)
        return speed1,speed2

    def _angle_to_QP(self,angle):
        range_min=0
        range_max=221
        angle_min=0
        angle_max=45
        a1=angle - angle_min
        a2=range_max - range_min
        a3=angle_max - angle_min
        angle = int((a1 *a2)/a3 + range_min)
        return angle
        
    def check_lowest_speeds(self,seconds):
        minspeedM1= np.Inf
        minspeedM2= np.Inf
        print("Wait two seconds before sending the ball. Film and measure landing position")
        sleep(2)
        for _ in range(0,int(seconds*10)):
            speed1 = self.rc.ReadSpeedM1(self.address[0])
            speed2 = self.rc.ReadSpeedM2(self.address[0])
            if(speed1[0]):
                if speed1[1]<minspeedM1: minspeedM1= speed1[1]
            if(speed2[0]):
                if speed2[1]<minspeedM2: minspeedM2= speed2[1]
            sleep(0.1)
        return minspeedM1,minspeedM2

    def _calculate_spin(QPPS1,QPPS2,speed,spin):
        print(QPPS1,QPPS2)
        radius = 0.1
        encoder_pulses_per_rad = 1024*(180/3.14)/360
        angular_speed1=QPPS1/encoder_pulses_per_rad
        angular_speed2=QPPS2/encoder_pulses_per_rad
        print(angular_speed1,angular_speed2)
        real_spin=((angular_speed2-speed/radius*3.95*1.0)-(angular_speed1-speed/radius*3.95*1.0))/(2*1000*1.0)
        print(real_spin)
        return real_spin

    def calibrate_motor_constants(self,landingpoint,flag,set_speed,set_angle,spin=0,speedM1=0,speedM2=0, tf=0):
        real_speed, real_spin = self.optim.calculate_real_speed(landingpoint, set_speed, set_angle, spin, tf)
        if flag:
            if spin!=0: self.spin_constant=spin/real_spin*self.spin_constant
            self.M1speedconst=(set_speed/real_speed)*self.M1speedconst
            self.M2speedconst=(set_speed/real_speed)*self.M2speedconst #Because the constant is used in the calibration shot
        else:
            if spin!=0: self.spin_constant=(self._calculate_spin(speedM1,speedM2,set_speed,spin)/real_spin)*self.spin_constant
            minspeedM1,minspeedM2=self._QPPS_to_speed(speedM1,speedM2)
            self.M1speedconst=(minspeedM1/real_speed)*self.M1speedconst
            self.M2speedconst=(minspeedM2/real_speed)*self.M2speedconst
        return  self.M1speedconst, self.M2speedconst, self.spin_constant

    def reset_calibration_constants(self):
        self.M1speedconst=1.0
        self.M2speedconst=1.0
        self.spin_constant=1.0
        return self.M1speedconst, self.M2speedconst, self.spin_constant

    def manuell_shot(self,speed,angle,spin=0,dispenser_speed=120):
        print("Set_angle: ",angle)
        angle = self._angle_to_QP(angle)
        print("Target position M1:", angle)

        self.rc.SpeedAccelDeccelPositionM1(self.address[1],10,20,10,angle,0)
        self.has_angle_motor_stopped_moving() #sleep(5)

        speedm1,speedm2=self._speed_to_QPPS(speed,spin)
        self.rc.SpeedAccelM1(self.address[0],84000,int(speedm1))
        self.rc.SpeedAccelM2(self.address[0],84000,int(speedm2))
        self.rc.ForwardM2(self.address[1],dispenser_speed)


    def shot_done(self):
        self.rc.SpeedAccelM2(self.address[0],84000,0)
        self.rc.SpeedAccelM1(self.address[0],84000,0)
        self.rc.ForwardM2(self.address[1],0)
        #Two ways to return to 0 degrees:
        backward_speed = 126 #range: 0-126
        self.rc.BackwardM1(self.address[1],backward_speed)
        self.has_angle_motor_stopped_moving()
        self.rc.BackwardM1(self.address[1],0)
        self.rc.ResetEncoders(self.address[1])
        #or: self.rc.SpeedAccelDeccelPositionM1(self.address[1],10,20,10,0,0) this may cause error sometimes.

    def landing_shot(self,target,dispenser_speed):
        speed,rad_angle,spin,tf= self.optim.find_initvalues_spin(target)
        #The path may be plotted: self.optim.plot_path(speed,rad_angle,spin)

        degree_angle= rad_angle*180/np.pi
        enc_angle = self._angle_to_QP(degree_angle)
        print("Target position M1:", enc_angle)
        
        self.rc.SpeedAccelDeccelPositionM1(self.address[1],10,20,10,enc_angle,0)
        self.has_angle_motor_stopped_moving() 

        if target[0]==0:spin=0
        speedm1,speedm2=self._speed_to_QPPS(speed,spin)     
        
        self.rc.SpeedAccelM1(self.address[0],84000,speedm1)
        self.rc.SpeedAccelM2(self.address[0],84000,speedm2)
        self.rc.ForwardM2(self.address[1],dispenser_speed)
        return speed,degree_angle,spin,speedm1,speedm2

    def get_motor_constants(self):
        return self.M1speedconst,self.M2speedconst,self.spin_constant

