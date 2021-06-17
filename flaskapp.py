#import serial
from flask import Flask, render_template, request, session, redirect, url_for
from footballmachine import Footballmachine
from time import sleep
from threading import Thread
import numpy as np

# Glabal variables
fm = Footballmachine()

# Initialize web app and error handlers
app = Flask(__name__)
app.secret_key = b'prosoccertrainer2021'
app.debug = True
@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500
app.register_error_handler(500, page_not_found)

# Define endpoints
@app.route('/', methods = ['POST', 'GET'])
def index():
    if request.method == 'GET':
        return render_template('index.html')

@app.route('/reset')
def reset():
    if request.method == 'GET':
        fm.init_motors()
        return redirect(url_for('index'))
        
@app.route('/calib1')
def calib1():
    if request.method == 'GET':
        session.clear()
        m1const,m2const,spinconst = fm.get_calibration_constants()
        session["M1const"]=m1const
        session["M2const"]=m2const
        session["Spinconst"]=spinconst
        return render_template('calib1.html', form=session)

@app.route('/calib2', methods = ['POST', 'GET'])
def calib2():
    if request.method == 'GET':
        return f"The URL /calib2 is accessed directly. Try going to '/calib1' to calibrate."

    if request.method == 'POST': 
        if request.form['submit_button'] == 'Test shot':
            missing_values =list() 
            dispenser_valid =1
            target_valid=1
            feedback = ""
            req = request.form
            missing_values=[]
            for k, v in req.items():
                    if v == "":
                        missing_values.append(k)
                    else:
                        if (k=="target"): 
                            target_list = v.split(",")                            
                            if not len(target_list) == 3:
                                target_valid=0
                            else: 
                                for i in range(0,3):
                                    if not target_list[i].isdigit():
                                        try:
                                            target_list[i]=float(target_list[i])
                                        except ValueError:
                                            # Handle case if user type in brackets [X,Y,Z] in a new try/expect ValueError
                                            # numstring= ""
                                            # numstring.join(k for k in target_list[i] if k.isdigit() or k==".")
                                            # target_list[i]=float(numstring) 
                                            target_valid=0
                                            break
                                    else: target_list[i]=float(target_list[i]) 
                                if target_valid and len(target_list) == 3: target_valid=1
                                else: target_valid = 0
                            print("Target: ", target_list)

                        if (k=="dispenser_speed"): 
                            dispenser_valid=valid_dispenser_speed(int(request.form['dispenser_speed']))
                    
            if missing_values:
                feedback = f"Missing fields for {', '.join(missing_values)}"
                return render_template('calib1.html',feedback=feedback,form=session)
            if not target_valid:
                feedback = f"{request.form['target']} is not a valid target. Enter a positive target within 30m radius inf this format: X,Y,Z."
                return render_template('calib1.html',feedback=feedback,form=session)
            if not dispenser_valid:
                feedback = f"{request.form['dispenser_speed']} is not a valid dispenser speed. Enter a valid dispenserspeed within range 1-126 degrees"
                return render_template('calib1.html',feedback=feedback, form=session)
            else:
                target=target_list
                session["Target"]=target
                session["Dispenser Speed"]=int(request.form["dispenser_speed"])
                flag,speed,angle,spin,speedm1,speedm2=fm.calibrate_shot(target,int(request.form["dispenser_speed"]))
                # sleep(10)
                minSpeedM1,minSpeedM2 = fm.check_lowest_speeds(10)
                session["MinSpeedM1"]=minSpeedM1
                session["MinSpeedM2"]=minSpeedM2
                fm.shot_done()
                session["Speed"]=speed
                session["Setspeed M1"]=speedm1
                session["Setspeed M2"]=speedm2
                session["Angle"]=angle
                session["Spin"]=spin
                #This return the "real constants"
                m1const,m2const,spinconst = fm.get_calibration_constants()
                session["Previous M1const"]=m1const
                session["Previous M2const"]=m2const
                session["Previous spinconst"]=spinconst
                
                return render_template('calib2.html')

        if request.form['submit_button'] == 'Reset calibration constants':
            session.clear()
            m1const,m2const, spinconst= fm.set_calibration_constants(1,1,1)
            m1const,m2const, spinconst= fm.get_calibration_constants()
            session["M1const"]=m1const
            session["M2const"]=m2const
            session["Spinconst"]=spinconst
            return render_template('calibrationdone.html',form=session)
                
@app.route('/calibrationdone', methods = ['POST', 'GET'])
def calibrationdone():
    if request.method == 'GET':
         return f"The URL /data is accessed directly. Try going to '/form' to submit form"

    if request.method == 'POST': 
        if request.form['submit_button'] == 'Calibrate':
            missing_values =list() 
            target_valid =1
            target_list=[]
            feedback = ""
            req = request.form
            for k, v in req.items():
                if v == "":
                    missing_values.append(k)
                else:
                    if (k=="landingpoint"): 
                        target_list = v.split(",")
                        
                        if not len(target_list) == 3:
                            target_valid=0
                        else: 
                            for i in range(0,3):
                                if not target_list[i].isdigit():
                                    try:
                                        target_list[i]=float(target_list[i]) 
                                    except ValueError:
                                        # Handle case if user type in brackets [X,Y,Z] in a new try/expect ValueError
                                        # numstring= ""
                                        # numstring.join(k for k in target_list[i] if k.isdigit() or k==".")
                                        # target_list[i]=float(numstring) 
                                        target_valid=0
                                        break
                                else: target_list[i]=float(target_list[i]) 
                            if target_valid and len(target_list) == 3: target_valid=1
                            else: target_valid = 0
                        print("Landingpoint: ", target_list)

                    
            if missing_values:
                feedback = f"Missing fields for {', '.join(missing_values)}"
                return render_template('calib2.html',feedback=feedback)
            if not target_valid:
                feedback = f"{request.form['landingpoint']} is not a valid target. Enter a positive target within 30m radius inf this format: X,Y,Z."
                return render_template('calib2.html',feedback=feedback)
            else:
                landingpoint=target_list
                #To calibrate without real measurements: 
                m1const,m2const, spinconst=fm.calibrate_motor_constants(session["Target"],landingpoint,1,session["Speed"],session["Angle"],session["Spin"],session["Setspeed M1"],session["Setspeed M2"])
                #To calibrate without real measurements (not recommended, consider future work): 
                #m1const,m2const,spinconst =fm.calibrate_motor_constants(session["Target"],landingpoint,0,session["Speed"],session["Angle"],session["Spin"],session["MinSpeedM1"],session["MinSpeedM2"])
                session["Landing point"]=landingpoint
                session["M1const"]=m1const
                session["M2const"]=m2const
                session["Spinconst"]=spinconst
                fm.set_calibration_constants(m1const,m2const,spinconst)
                return render_template('calibrationdone.html',form=session)

@app.route('/repeat')
def repeat():
    if request.method == 'GET':
        flag,speed,angle,spin,speedm1,speedm2=fm.landing_shot(session["Target"],session["Dispenser Speed"])
        # sleep(10)
        minSpeedM1,minSpeedM2 = fm.check_lowest_speeds(10)
        session["MinSpeedM1"]=minSpeedM1
        session["MinSpeedM2"]=minSpeedM2
        session["Speed"]=speed
        session["Angle"]=angle
        session["Spin"]=spin
        #This return the "real constants"
        m1const,m2const,spinconst = fm.get_calibration_constants()
        session["M1const"]=m1const
        session["M2const"]=m2const
        session["Spinconst"]=spinconst
        fm.shot_done()
        return render_template('data.html',form= session)

@app.route('/setcalib', methods = ['POST', 'GET'])
def setcalib():
    if request.method == 'GET':
        session.clear()
        m1const,m2const,spinconst = fm.get_calibration_constants()
        session["M1const"]=m1const
        session["M2const"]=m2const
        session["Spinconst"]=spinconst
        return render_template('setcalib.html', form=session)

    if request.method == 'POST':
        if request.form['submit_button'] == 'Set calibration constants':
                session.clear()
                print(request.form['M1const'],request.form['M2const'],request.form['spinconst'])
                m1const,m2const, spinconst= fm.set_calibration_constants(request.form['M1const'],request.form['M2const'],request.form['spinconst'])
                print(m1const,m2const, spinconst)
                session["M1const"]=m1const
                session["M2const"]=m2const
                session["spinconst"]=spinconst
                return render_template('calibrationdone.html',form=session)

@app.route('/target')
def target():
    if request.method == 'GET':
        session.clear()
        m1const,m2const,spinconst = fm.get_calibration_constants()
        session["M1const"]=m1const
        session["M2const"]=m2const
        session["Spinconst"]=spinconst
        return render_template('target.html', form=session)
        
        
@app.route('/manual')
def manual():
    if request.method == 'GET':
        session.clear()
        return render_template('manual.html')
        

@app.route('/data', methods = ['POST', 'GET'])
def data():
    if request.method == 'GET':
        return f"The URL /data is accessed directly."

    if request.method == 'POST':
        
        if request.form['submit_button'] == 'Shoot':
            missing_values =list() 
            speed_valid =1
            angle_valid =1
            spin_valid = 1
            dispenser_valid =1
            feedback = ""
            req = request.form
            for k, v in req.items():
                if v == "":
                    missing_values.append(k)
                else:
                    if (k=="angle"): 
                        try:
                            angle=float(request.form['angle'])
                            angle_valid=valid_angle(angle)
                        except ValueError:
                            angle_valid=0   
                    if (k=="speed"): 
                        try:
                            speed=float(request.form['speed'])
                            speed_valid=valid_speed(speed)
                        except ValueError:
                            speed_valid=0 
                    if (k=="dispenser_speed"): 
                        try:
                            dispenser_speed=int(request.form['dispenser_speed'])
                            dispenser_valid=valid_dispenser_speed(dispenser_speed)
                        except ValueError:
                            dispenser_valid=0 
                    if (k=="spin"): 
                        try:
                            spin=float(request.form['spin'])
                            spin_valid=valid_spin(spin)
                        except ValueError:
                            spin_valid=0
                            
            if missing_values:
                feedback = f"Missing fields for {', '.join(missing_values)}"
                return render_template('manual.html',feedback=feedback)
            if not speed_valid:
                feedback = f"{request.form['speed']} is not a valid speed. Enter a valid speed within range 0-17 m/s"
                return render_template('manual.html',feedback=feedback)
            if not angle_valid:
                feedback = f"{request.form['angle']} is not a valid angle. Enter a valid angle within range 5-45 degrees"
                return render_template('manual.html',feedback=feedback)
            if not dispenser_valid:
                feedback = f"{request.form['dispenser_speed']} is not a valid dispenser speed. Enter a valid dispenserspeed within range 1-126 degrees"
                return render_template('manual.html',feedback=feedback)
            if not spin_valid:
                feedback = f"{request.form['spin']} is not a valid spin. Enter a valid dispenserspeed within range -0.018-0.018 degrees"
                return render_template('manual.html',feedback=feedback)
            else:
                speed=float(request.form["speed"])
                angle=float(request.form["angle"])
                dispenser_speed=int(request.form["dispenser_speed"])
                spin=float(request.form["spin"])
                flag = fm.manual_shot(speed,angle,spin,dispenser_speed)
                if flag:
                    # sleep(10)
                    minSpeedM1,minSpeedM2 = fm.check_lowest_speeds(10)
                    session["MinSpeedM1"]=minSpeedM1
                    session["MinSpeedM2"]=minSpeedM2
                    fm.shot_done()
                    session["Speed"]=int(request.form["speed"])
                    session["Angle"]=int(request.form["angle"])
                    session["Dispenser Speed"]=int(request.form["dispenser_speed"])
                    m1const,m2const,spinconst = fm.get_calibration_constants()
                    session["M1const"]=m1const
                    session["M2const"]=m2const
                    session["Spinconst"]=spinconst
                else:
                    fm.shot_done()
                    feedback = f"{request.form['spin']} is a too high spin for the requested speed. Resulted in negative speeds. Try a lower spin or higher speed or lowering the spin constant manualy."
                    return render_template('manual.html',feedback=feedback)
                return render_template('data.html',form= session)

        if request.form['submit_button'] == 'Shoot landingball':
            missing_values =list() 
            target_valid =1
            dispenser_valid =1
            feedback = ""
            req = request.form
            for k, v in req.items():
                if v == "":
                    missing_values.append(k)
                else:
                    if (k=="target"): 
                        target_list = v.split(",")
                        if not len(target_list) == 3:
                            target_valid=0
                        else: 
                            for i in range(0,3):
                                if not target_list[i].isdigit():
                                    try:
                                        target_list[i]=float(target_list[i])
                                    except ValueError:
                                        # Handle case if user type in brackets [X,Y,Z] in a new try/expect ValueError
                                        # numstring= ""
                                        # numstring.join(k for k in target_list[i] if k.isdigit() or k==".")
                                        # target_list[i]=float(numstring) 
                                        target_valid=0
                                        break
                                else: target_list[i]=float(target_list[i]) 
                            if target_valid and len(target_list) == 3: target_valid=1
                            else: target_valid = 0
                        print("Target: ", target_list)

                    if (k=="dispenser_speed"): 
                        dispenser_valid=valid_dispenser_speed(int(request.form['dispenser_speed']))
                    
            if missing_values:
                feedback = f"Missing fields for {', '.join(missing_values)}"
                return render_template('target.html',feedback=feedback,form=session)
            if not target_valid:
                feedback = f"{request.form['target']} is not a valid target. Enter a positive target within 30m radius inf this format: X,Y,Z."
                return render_template('target.html',feedback=feedback,form=session)
            if not dispenser_valid:
                feedback = f"{request.form['dispenser_speed']} is not a valid dispenser speed. Enter a valid dispenserspeed within range 1-126 degrees"
                return render_template('target.html',feedback=feedback,form=session)
            else:
                target=target_list
                session["Target"]=target
                session["Dispenser Speed"]=int(request.form["dispenser_speed"])
                flag,speed,angle,spin,speedm1,speedm2=fm.landing_shot(target,int(request.form["dispenser_speed"]))
                if flag:
                    # sleep(10)
                    minSpeedM1,minSpeedM2 = fm.check_lowest_speeds(10)
                    session["MinSpeedM1"]=minSpeedM1
                    session["MinSpeedM2"]=minSpeedM2
                    session["Speed"]=speed
                    session["Angle"]=angle
                    session["Spin"]=spin
                    #This return the "real constants"
                    m1const,m2const,spinconst = fm.get_calibration_constants()
                    session["M1const"]=m1const
                    session["M2const"]=m2const
                    session["Spinconst"]=spinconst
                    fm.shot_done()
                else:
                    fm.shot_done()
                    feedback = f"Selected landing point is out of range. Resulted in negative speeds. Try a lower spin or higher speed or lowering the spin constant manualy."
                    return render_template('target.html',feedback=feedback)
                return render_template('data.html',form= session)

# Utilities
def valid_speed(speed):
    return (speed>=1 and speed<=17) 
def valid_angle(angle):
    return (angle>=0 and angle<=45)
def valid_dispenser_speed(dispenser_speed):
    return (dispenser_speed>=1 and dispenser_speed<=126)
def valid_spin(spin):
    return (spin>=-0.043 and spin<=0.043) #More spin can be allowed. 0.43 can land 0.25m on xaxis

if __name__ == '__main__':
   app.run()
