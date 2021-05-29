import serial
from flask import Flask, render_template, request
from control_code import Footballmachine
from time import sleep
from threading import Thread
import numpy as np

# Glabal variables
fm = Footballmachine()
ball_data ={}
# Initialize web app and error handlers
app = Flask(__name__)
app.debug = True
@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500
app.register_error_handler(500, page_not_found)

# Define endpoints
@app.route('/', methods = ['POST', 'GET'])
def index():
    if request.method == 'GET':
        fm.init_motors()
        return render_template('index.html')

        
@app.route('/calib1')
def calib1():
    if request.method == 'GET':
        return render_template('calib1.html')

@app.route('/calib2')
def calib2():
    if request.method == 'GET':
         return f"The URL /data is accessed directly. Try going to '/form' to submit form"

    if request.method == 'POST': 
        if request.form['submit_button'] == 'Test shot':
            ball_data = {}
            missing_values =list() 
            speed_valid =1
            angle_valid =1
            dispenser_valid =1
            feedback = ""
            req = request.form
            for k, v in req.items():
                if v == "":
                    missing_values.append(k)
                else:
                    if (k=="angle"): 
                        angle_valid=valid_angle(int(request.form['angle']))
                    if (k=="speed"): 
                        speed_valid=valid_speed(int(request.form['speed']))
                    if (k=="dispenser_speed"): 
                        dispenser_valid=valid_dispenser_speed(int(request.form['dispenser_speed']))
                    
            if missing_values:
                feedback = f"Missing fields for {', '.join(missing_values)}"
                return render_template('calib1.html',feedback=feedback)
            if not speed_valid:
                feedback = f"{request.form['speed']} is not a valid speed. Enter a valid speed within range 0-27 m/s"
                return render_template('calib1.html',feedback=feedback)
            if not angle_valid:
                feedback = f"{request.form['angle']} is not a valid angle. Enter a valid angle within range 5-45 degrees"
                return render_template('calib1.html',feedback=feedback)
            if not dispenser_valid:
                feedback = f"{request.form['dispenser_speed']} is not a valid dispenser speed. Enter a valid dispenserspeed within range 1-126 degrees"
                return render_template('calib1.html',feedback=feedback)
            else:
                speed=int(request.form["speed"])
                angle=int(request.form["angle"])
                dispenser_speed=int(request.form["dispenser_speed"])
                fm.manuell_shot(speed,angle,dispenser_speed)
                minSpeedM1,minSpeedM2 = fm.check_lowest_speeds(10)
                fm.manuell_shot_done()
                ball_data["MinSpeedM1"]=minSpeedM1
                ball_data["MinSpeedM2"]=minSpeedM2
                ball_data["Speed"]=int(request.form["speed"])
                ball_data["Angle"]=int(request.form["angle"])
                ball_data["Dispenser Speed"]=int(request.form["dispenser_speed"])
                return render_template('calib2.html')

                
@app.route('/calibrationdone')
def calibrationdone():
    if request.method == 'GET':
         return f"The URL /data is accessed directly. Try going to '/form' to submit form"

    if request.method == 'POST': 
        if request.form['submit_button'] == 'Calibrate':
            ball_data = {}
            missing_values =list() 
            target_valid =1
            feedback = ""
            req = request.form
            for k, v in req.items():
                if v == "":
                    missing_values.append(k)
                else:
                    if (k=="target"): 
                        target_list = v.split(",")
                        print(target_list)
                        if not len(target_list) == 3:
                            target_valid=0
                        else: 
                            for i in range(0,3):
                                print(target_list[i].isdigit())
                                if not target_list[i].isdigit():
                                    integerstring= ""
                                    integerstring.join(k for k in target_list[i] if k.isdigit())
                                    if target_list[i].isdigit():
                                        target_list[i]=int(integerstring) 
                                    else: 
                                        target_valid=0
                                        break
                                else: target_list[i]=int(target_list[i]) 
                            if target_valid and len(target_list) == 3: target_valid=1
                            else: target_valid = 0
                        print(target_list)

                    
            if missing_values:
                feedback = f"Missing fields for {', '.join(missing_values)}"
                return render_template('calib2.html',feedback=feedback)
            if not target_valid:
                feedback = f"{request.form['target']} is not a valid target. Enter a positive target within 30m radius inf this format: X,Y,Z."
                return render_template('calib2.html',feedback=feedback)
            else:
                target=[int(target_list[0]),int(target_list[1]),int(target_list[2])]
                m1const,m2const =fm.calibrate_motor_constants(target,ball_data["Speed"],ball_data["Angle"],ball_data["MinSpeedM1"],ball_data["MinSpeedM2"])
                ball_data["M1const"]=m1const
                ball_data["M2const"]=m2const
                return render_template('calibrationdone.html',form=ball_data)


@app.route('/landing')
def landing():
    if request.method == 'GET':
        return render_template('landingspunkt.html')
        
@app.route('/manuell')
def manuell():
    if request.method == 'GET':
        return render_template('manuell.html')
        

@app.route('/data', methods = ['POST', 'GET'])
def data():
    if request.method == 'GET':
        return f"The URL /data is accessed directly. Try going to '/form' to submit form"

    if request.method == 'POST':
        
        if request.form['submit_button'] == 'Shoot':
            ball_data = {}
            missing_values =list() 
            speed_valid =1
            angle_valid =1
            dispenser_valid =1
            feedback = ""
            req = request.form
            for k, v in req.items():
                if v == "":
                    missing_values.append(k)
                else:
                    if (k=="angle"): 
                        angle_valid=valid_angle(int(request.form['angle']))
                    if (k=="speed"): 
                        speed_valid=valid_speed(int(request.form['speed']))
                    if (k=="dispenser_speed"): 
                        dispenser_valid=valid_dispenser_speed(int(request.form['dispenser_speed']))
                    
            if missing_values:
                feedback = f"Missing fields for {', '.join(missing_values)}"
                return render_template('manuell.html',feedback=feedback)
            if not speed_valid:
                feedback = f"{request.form['speed']} is not a valid speed. Enter a valid speed within range 0-27 m/s"
                return render_template('manuell.html',feedback=feedback)
            if not angle_valid:
                feedback = f"{request.form['angle']} is not a valid angle. Enter a valid angle within range 5-45 degrees"
                return render_template('manuell.html',feedback=feedback)
            if not dispenser_valid:
                feedback = f"{request.form['dispenser_speed']} is not a valid dispenser speed. Enter a valid dispenserspeed within range 1-126 degrees"
                return render_template('manuell.html',feedback=feedback)
            else:
                speed=int(request.form["speed"])
                angle=int(request.form["angle"])
                dispenser_speed=int(request.form["dispenser_speed"])
                fm.manuell_shot(speed,angle,dispenser_speed)
                sleep(10)
                fm.manuell_shot_done()
                ball_data["Speed"]=int(request.form["speed"])
                ball_data["Angle"]=int(request.form["angle"])
                ball_data["Dispenser Speed"]=int(request.form["dispenser_speed"])
                return render_template('data.html',form= ball_data)

        if request.form['submit_button'] == 'Shoot landingball':
            ball_data = {}
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
                        print(target_list)
                        if not len(target_list) == 3:
                            target_valid=0
                        else: 
                            for i in range(0,3):
                                print(target_list[i].isdigit())
                                if not target_list[i].isdigit():
                                    integerstring= ""
                                    integerstring.join(k for k in target_list[i] if k.isdigit())
                                    if target_list[i].isdigit():
                                        target_list[i]=int(integerstring) 
                                    else: 
                                        target_valid=0
                                        break
                                else: target_list[i]=int(target_list[i]) 
                            if target_valid and len(target_list) == 3: target_valid=1
                            else: target_valid = 0
                        print(target_list)

                    if (k=="dispenser_speed"): 
                        dispenser_valid=valid_dispenser_speed(int(request.form['dispenser_speed']))
                    
            if missing_values:
                feedback = f"Missing fields for {', '.join(missing_values)}"
                return render_template('landingspunkt.html',feedback=feedback)
            if not target_valid:
                feedback = f"{request.form['target']} is not a valid target. Enter a positive target within 30m radius inf this format: X,Y,Z."
                return render_template('landingspunkt.html',feedback=feedback)
            if not dispenser_valid:
                feedback = f"{request.form['dispenser_speed']} is not a valid dispenser speed. Enter a valid dispenserspeed within range 1-126 degrees"
                return render_template('landingspunkt.html',feedback=feedback)
            else:
                target=[int(target_list[0]),int(target_list[1]),int(target_list[2])]
                ball_data["Target"]=request.form["target"]
                ball_data["Dispenser Speed"]=int(request.form["dispenser_speed"])
                speed,angle,spin=fm.landing_shot(target,int(request.form["dispenser_speed"]))
                sleep(10)
                ball_data["Speed"]=speed
                ball_data["Angle"]=angle
                ball_data["Spin"]=spin
                fm.manuell_shot_done()
                return render_template('data.html',form= ball_data)

# Utilities
def valid_speed(speed):
    return (speed>=1 and speed<=27) 
def valid_angle(angle):
    return (angle>=0 and angle<=45)
def valid_dispenser_speed(dispenser_speed):
    return (dispenser_speed>=1 and dispenser_speed<=126)

def mock_get_optim_values(X,Y,Z,spin=False):
    return 10,45*np.pi/180,0

def mock_calculate_real_speed(X,Y,Z,speed,angle):
    return speed-0.3