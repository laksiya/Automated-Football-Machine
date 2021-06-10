def _speed_to_QPPS(speed,spin=0):
    spin_constant=1.0
    radius=0.1
    M1speedconst=1.0
    M2speedconst=1.0
    encoder_pulses_per_rad=1024
    speedconst = 0.325
    flag=1
    ang_speed_spin=spin*100*spin_constant
    max_spin=speed/radius*speedconst*M1speedconst

    print("angspeed1: ",speed/radius*speedconst*M1speedconst)
    print("angspeed2: ",speed/radius*speedconst*M2speedconst)
    print("angspeed:", ang_speed_spin)

    angular_speed1=speed/radius*speedconst*M1speedconst-ang_speed_spin
    angular_speed2=speed/radius*speedconst*M2speedconst+ang_speed_spin
    # if angular_speed1 <0: 
    #     angular_speed1=speed/radius*3.25*M1speedconst
    #     angular_speed2=speed/radius*3.25*M2speedconst+spin*1000*spin_constant*2
    # if angular_speed2 <0: 
    #     angular_speed2=speed/radius*3.25*M2speedconst
    #     angular_speed1=speed/radius*3.25*M1speedconst+spin*1000*spin_constant*2
    if angular_speed1 <=0 or angular_speed1>87.1: 
        flag=0
        angular_speed1=0
    if angular_speed2 <=0 or angular_speed2>87.1: 
        flag=0
        angular_speed2=0 #5m/s to get the ball out.
    
    print(angular_speed1,angular_speed2)
    QPPS1= encoder_pulses_per_rad*angular_speed1*2
    QPPS2= encoder_pulses_per_rad*angular_speed2*2
    print(QPPS1,QPPS2)
    if QPPS1>178401: QPPS1=178401 #184879
    if QPPS2>178401: QPPS2=178401
    return flag,round(QPPS1), round(QPPS2)


def _1speed_to_QPPS(speed,spin=0):
        radius = 0.1
        encoder_pulses_per_rad = 1024*(180/3.14)/360
        angular_speed1=speed/radius*4.05*1.0-spin*100*1.0
        angular_speed2=speed/radius*4.05*1.0+spin*100*1.0
        print(angular_speed1,angular_speed2)
        flag=1
        QPPS1= encoder_pulses_per_rad*angular_speed1
        QPPS2= encoder_pulses_per_rad*angular_speed2
        print(QPPS1,QPPS2)
        if QPPS1>178401 or QPPS1<0:
            flag =0
        if QPPS2>178401 or QPPS2<0:
            flag=0
        return flag,round(QPPS1), round(QPPS2)

def _speed_to_QPPS(speed,spin=0):
        radius = 0.1
        M1speedconst=1.0
        M2speedconst=1.0
        spin_constant=1.0
        flag=1
        encoder_pulses_per_rad = 1024*(180/3.14)/360
        angular_speed1=speed/radius*3.198*M1speedconst-spin*1000*spin_constant
        angular_speed2=speed/radius*3.198*M2speedconst+spin*1000*spin_constant
        print(angular_speed1,angular_speed2)
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


speed=17
spin=0
print(_speed_to_QPPS(speed,spin))