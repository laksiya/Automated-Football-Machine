from roboclaw_3 import Roboclaw
from time import sleep
from numpy import pi

class Footballmachine:
    def __init__(self,address=0x80,baudrate=38400,port="/dev/ttyS0"):
        self.address = address
        self.rc = Roboclaw(port, baudrate)
        self.rc.Open()
        version = self.rc.ReadVersion(self.address)
        if version[0]==False:
            print("GETVERSION Failed - check power supply and conections")
            return
        else:
            print(repr(version[1]))

    def has_angle_motor_stopped_moving(self):
        interval = 1
        first = self.rc.ReadEncM1(self.address)
        sleep(interval)
        second = self.rc.ReadEncM1(self.address)
        while(first!=second): 
            first = self.rc.ReadEncM1(self.address)
            sleep(interval)
            second = self.rc.ReadEncM1(self.address)

    def init_motors(self):
        print("Initializing all motors...")
        self.rc.BackwardM1(self.address,126)
        self.has_angle_motor_stopped_moving()
        self.rc.BackwardM1(self.address,0)
        self.rc.ResetEncoders(self.address)
        print("Angle encoder:", self.rc.ReadEncM1(self.address)[1])      

    def displayspeed(self):
        enc1 = self.rc.ReadEncM1(self.address)
        enc2 = self.rc.ReadEncM2(self.address)
        speed1 = self.rc.ReadSpeedM1(self.address)
        speed2 = self.rc.ReadSpeedM2(self.address)

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

    def speed_to_QPPS(self,speed):
        radius = 0.1
        encoder_pulses_per_rad = 1024/2
        angular_speed=speed/(2*pi*radius)
        QPPS=encoder_pulses_per_rad*angular_speed
        return int(QPPS)

    def angle_to_QP(self,angle):
        range_min=0
        range_max=225
        angle_min=0
        angle_max=55
        a1=int(angle) - angle_min
        a2=range_max - range_min
        a3=angle_max - angle_min
        angle = int((a1 *a2)/a3 + range_min)
        return angle

    def set_angle(self,angle):
        print("Set_angle: ",angle)
        angle = self.angle_to_QP(angle)
        print("Target position M1:", angle)
        self.rc.SpeedAccelDeccelPositionM1(self.address,10,10,10,angle,0)
        self.has_angle_motor_stopped_moving()
        print("Angle encoder:", self.rc.ReadEncM1(self.address)[1])

    def set_speed_then_stop(self,speed):
        print("Set_speed: ",speed)
        speed=self.speed_to_QPPS(int(speed))
        self.rc.SpeedAccelM2(self.address,22000,speed)
        sleep(4)
        self.rc.SpeedAccelM2(self.address,22000,0)

    def set_speed(self,speed):
        print("Set_speed: ",speed)
        speed=self.speed_to_QPPS(int(speed))
        self.rc.SpeedAccelM2(self.address,22000,speed)
        for i in range(0,50):
            print(("{} # ".format(i)), end=' ')
            self.displayspeed() 
            sleep(0.1)

    def check_encoders(self,seconds):
        for i in range(0,seconds):
            print(("{} # ".format(i)), end=' ')
            self.displayspeed() 
            sleep(0.1)

   