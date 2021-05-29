
def set_speedM1(self,spin):
        #speedreached=False
        quadspeed=int(round(spin*4000))
        print(quadspeed)
        self.Robo.mutex.acquire()               
        self.Robo.SetM1Speed(quadspeed)
        self.Robo.mutex.release()       
        return True
    
def set_speedM2(self,spin):             
    quadspeed=int(round(spin*4000))
    print(quadspeed)
    self.Robo.mutex.acquire()
    self.Robo.SetM2Speed(quadspeed)
    self.Robo.mutex.release()
    return True
        
def set_speed_ball(self,velocity):
    
    spinM1=self.calibM1*spin
    spinM2=self.calibM2*spin
    if spinM1<-184879 or spinM2<-178401:
        print("speed is to high!")
        return False
    flagM1=self.set_speedM1(spinM1)
    flagM2=self.set_speedM2(spinM2)
    if not flagM1 and flagM2:
        return False
    return True

def _speed_to_QPPS(speed):
    angular_speed=speed/(0.1*2*3.14)
    QPPS=int(round(angular_speed*4000))
    return QPPS   

def _1speed_to_QPPS(speed):
        radius = 0.1
        encoder_pulses_per_rad = 1024/2
        angular_speed=speed/(2*3.14*radius)
        QPPS=encoder_pulses_per_rad*angular_speed
        return QPPS
        
print(_speed_to_QPPS(27))