from roboclaw_3 import Roboclaw
from time import sleep
import numpy as np
from threading import Thread
from optimizer import Optimizer

class Footballmachine:
    def __init__(self,address=[0x80,0x81],baudrate=38400,port="/dev/ttyS0"):
        print("INITIALZING!!")
        self.address = address
        self.rc = Roboclaw(port, baudrate)
        self.rc.Open()
        self.spin_constant = 1.02
        self.M1speedconst=1.02
        self.M2speedconst=1.02
        self.optim=Optimizer()
        self.radius = 0.1
        self.encoder_pulses_per_rad = 1024*(180/3.14)/360

    def _has_angle_motor_stopped_moving(self):
        interval = 1
        first = int(self.rc.ReadEncM1(self.address[1])[1])
        sleep(interval)
        second = int(self.rc.ReadEncM1(self.address[1])[1])
        return first==second

    def init_motors(self):
        print("Resetting all motors...")
        print("Angle encoder:", self.rc.ReadEncM1(self.address[1])[1]) 
        self.rc.SpeedAccelM2(self.address[0],84000,0)
        self.rc.SpeedAccelM1(self.address[0],84000,0)
        self.rc.ForwardM2(self.address[1],0)
        backward_speed = 126 #range: 0-126
        self.rc.BackwardM1(self.address[1],backward_speed)
        sleep(2)
        goal_reached=False
        while goal_reached==False:
            goal_reached=self._has_angle_motor_stopped_moving() 
        print(self.M1speedconst,self.M2speedconst)
        self.rc.BackwardM1(self.address[1],0)
        self.rc.ResetEncoders(self.address[1])
        print("Angle encoder:", self.rc.ReadEncM1(self.address[1])[1]) 

    def _speed_to_QPPS(self,speed,spin=0,M1speedconst=0,M2speedconst=0):
        if M1speedconst!=0: 
            self.M1speedconst=M1speedconst
            self.M2speedconst=M2speedconst
        radius = 0.1
        flag=1
        encoder_pulses_per_rad = 1024*(180/3.14)/360
        angular_speed1=speed/radius*3.25*self.M1speedconst-spin*1000*self.spin_constant
        angular_speed2=speed/radius*3.25*self.M2speedconst+spin*1000*self.spin_constant
        print(angular_speed1,angular_speed2)
        print(self.M1speedconst,self.M2speedconst)
        QPPS1= encoder_pulses_per_rad*angular_speed1*2
        QPPS2= encoder_pulses_per_rad*angular_speed2*2
        print(QPPS1,QPPS2)
        if QPPS1>178401:
            flag =0
            QPPS1=178401
        if QPPS1<0:
            flag =0
            QPPS1=33000
        if QPPS2>178401:
            flag =0
            QPPS2=178401
        if QPPS2<0:
            flag =0
            QPPS2=33000
        return flag, round(QPPS1), round(QPPS2)   

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
        
    def calibrate_motor_constants(self,target,landingpoint,flag,set_speed,set_angle,spin=0,speedM1=0,speedM2=0, tf=0):
        real_speed, real_spin = self.optim.calculate_real_speed(landingpoint, set_speed, set_angle, spin, tf)
        real_spin=round(real_spin,4)
        print(f"(calculated by optim) real_speed {real_speed}, real_spin{real_spin} ")
        if flag:
            print(f"Target[0] was {target[0]}")
            print(f"Landingpoint was {landingpoint[0]}")

            #We wanted spin but we didnt get it at all(X=0, real_spin=0)
            if target[0]!=0 and landingpoint[0]==0 and set_speed/real_speed>=0.8 :
                self.spin_constant=2*self.spin_constant

            #We didnt want spin but we got it? spin=0 real_spin!=0 - this is out of scope
            elif target[0]==0 and real_spin!=0: 
                #Do not handle this spin issue
                self.M1speedconst=(set_speed/real_speed)*self.M1speedconst
                self.M2speedconst=(set_speed/real_speed)*self.M2speedconst 

            #We wanted spin but we didnt get enough(real_spin!=0)
            elif target[0]!=0 and set_speed/real_speed>=0.8 and real_spin!=0: 
                self.spin_constant=(spin*1000)/(real_spin*1000)*self.spin_constant
                
            else:
                self.M1speedconst=(set_speed/real_speed)*self.M1speedconst
                self.M2speedconst=(set_speed/real_speed)*self.M2speedconst #If the previous constant gives good results, keep it.
         #else:
            #This measurement based calibration needs improvment to work, but the other solution works fine.
            #if spin!=0: self.spin_constant=(self._calculate_spin(speedM1,speedM2,set_speed,spin)/real_spin)*self.spin_constant
            #minspeedM1,minspeedM2=self._QPPS_to_speed(speedM1,speedM2)
            #self.M1speedconst=(minspeedM1/real_speed)*self.M1speedconst
            #self.M2speedconst=(minspeedM2/real_speed)*self.M2speedconst         
        return  self.M1speedconst, self.M2speedconst, self.spin_constant

    def get_calibration_constants(self):
        return self.M1speedconst,self.M2speedconst,self.spin_constant

    def set_calibration_constants(self,valM1,valM2,valspin):
        if valM1!="":self.M1speedconst=float(valM1)
        if valM2!="":self.M2speedconst=float(valM2)
        if valspin!="":self.spin_constant=float(valspin)
        print("NEW CONSTANTS:", self.M1speedconst, self.M2speedconst, self.spin_constant)
        return self.M1speedconst, self.M2speedconst, self.spin_constant

    def manuell_shot(self,speed,angle,spin=0,dispenser_speed=120):
        print("Set_angle: ",angle)
        angle = self._angle_to_QP(angle)
        print("Target position M1:", angle)

        flag, speedm1,speedm2=self._speed_to_QPPS(speed,spin)
        if flag:
            self.rc.SpeedAccelDeccelPositionM1(self.address[1],5,5,5,angle,0)
            sleep(2)
            goal_reached=False
            while goal_reached==False:
                goal_reached=self._has_angle_motor_stopped_moving() 
            print(self.M1speedconst,self.M2speedconst)
            self.rc.SpeedAccelM2(self.address[0],84000,int(speedm1))
            self.rc.SpeedAccelM1(self.address[0],84000,int(speedm2))
            self.rc.ForwardM2(self.address[1],dispenser_speed)
        return flag

    def shot_done(self):
        self.rc.ForwardM2(self.address[1],0)
        self.rc.SpeedAccelM2(self.address[0],84000,0)
        self.rc.SpeedAccelM1(self.address[0],84000,0)
        self.rc.ForwardM2(self.address[0],0)
        self.rc.ForwardM1(self.address[0],0)
        

    def landing_shot(self,target,dispenser_speed):
        speed,rad_angle,spin,tf= self.optim.find_initvalues_spin(target)
        #The path may be plotted: self.optim.plot_path(speed,rad_angle,spin)

        degree_angle= rad_angle*180/np.pi
        enc_angle = self._angle_to_QP(degree_angle)
        print("Target position M1:", enc_angle)
    
        if target[0]==0:spin=0
        flag, speedm1,speedm2=self._speed_to_QPPS(speed,spin)     
        if flag:
            self.rc.SpeedAccelDeccelPositionM1(self.address[1],5,5,5,enc_angle,0)
            sleep(2)
            goal_reached=False
            while goal_reached==False:
                goal_reached=self._has_angle_motor_stopped_moving() 
            print(self.M1speedconst,self.M2speedconst)
            self.rc.SpeedAccelM1(self.address[0],84000,speedm1)
            self.rc.SpeedAccelM2(self.address[0],84000,speedm2)
            self.rc.ForwardM2(self.address[1],dispenser_speed)
        return flag,speed,degree_angle,spin,speedm1,speedm2

    def calibrate_shot(self,target,dispenser_speed):
        speed,rad_angle,spin,tf= self.optim.find_initvalues_spin(target)
        #The path may be plotted: self.optim.plot_path(speed,rad_angle,spin)

        degree_angle= rad_angle*180/np.pi
        enc_angle = self._angle_to_QP(degree_angle)
        print("Target position M1:", enc_angle)
        
        self.rc.SpeedAccelDeccelPositionM1(self.address[1],5,5,5,enc_angle,0)
        sleep(2)
        goal_reached=False
        while goal_reached==False:
            goal_reached=self._has_angle_motor_stopped_moving() 
        
        if target[0]==0:spin=0
        print(self.M1speedconst,self.M2speedconst)
        flag, speedm1,speedm2=self._speed_to_QPPS(speed,spin)     
        self.rc.SpeedAccelM2(self.address[0],84000,speedm2)
        self.rc.SpeedAccelM1(self.address[0],84000,speedm1)
        self.rc.ForwardM2(self.address[1],dispenser_speed)

        return flag,speed,degree_angle,spin,speedm1,speedm2




    def check_lowest_speeds(self,seconds):
            minspeedM1= np.Inf
            minspeedM2= np.Inf
            sleep(2)
            for _ in range(0,int(seconds*10)):
                speed1 = self.rc.ReadSpeedM1(self.address[0])
                speed2 = self.rc.ReadSpeedM2(self.address[0])
                if(speed1[0]):
                    if speed1[1]>0 and speed1[1]<minspeedM1: minspeedM1= speed1[1]
                if(speed2[0]):
                    if speed2[1]<minspeedM2: minspeedM2= speed2[1]
                sleep(0.1)
            return minspeedM1,minspeedM2

    def _calculate_spin(self,QPPS1,QPPS2,speed):
        print(QPPS1,QPPS2)
        angular_speed1=QPPS1/self.encoder_pulses_per_rad
        angular_speed2=QPPS2/self.encoder_pulses_per_rad
        print(angular_speed1,angular_speed2)
        lowest_spin=((angular_speed2-speed/self.radius*3.25*self.M1speedconst)-(angular_speed1-speed/self.radius*3.25*self.M2speedconst))/(2*1000*self.spin_constant)
        print(lowest_spin)
        return lowest_spin
