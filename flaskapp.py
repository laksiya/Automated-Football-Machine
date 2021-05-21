# Flask on Apache
# https://asdkazmi.medium.com/deploying-flask-app-with-wsgi-and-apache-server-on-ubuntu-20-04-396607e0e40f
# To get access to html folder: sudo chown (check out raspberrys how to apache site)
import serial
from flask import Flask, render_template, request
from control_code import Footballmachine
from datetime import datetime

fm = Footballmachine()
dict ={}
missing_values =list()
app = Flask(__name__)
@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500

app.register_error_handler(500, page_not_found)


@app.route('/', methods = ['POST', 'GET'])
def index():
    if request.method == 'GET':
        #fm.init_motors()
        return render_template('main.html')

    # if request.method == 'POST':
    #     print("POST MAIN.html")
    #     if request.form['submit_button'] == 'Test shot':
    #         print("POST ye.html")
    #         return render_template('main.html')
            #print("sbmit testshot mAIN.html")
            # fm.set_angle(int(request.form['angle']))
            # fm.set_speed(int(request.form['speed']))
            # fm.check_encoders(10)
            # fm.set_speed(0)
            

        # if request.form['submit_button'] == 'calibrate':
        #     # fm.set_angle(int(request.form['angle']))
        #     # fm.set_speed(int(request.form['speed']))
        #     # fm.check_encoders(int(request.form['seconds']))
        #     # fm.set_speed(0)
        #     form_data = request.form.copy()
        #     # form_data.add('expected encoder speed', set_speed)
        #     # form_data.add('motor lowest speed M1', minM1)
        #     # form_data.add('motor lowest speed M2', minM2)
        #     # #return render_template('data.html',form= form_data)
        #     return render_template('data.html',form= form_data)
        
        


@app.route('/data', methods = ['POST', 'GET'])
def data():
    if request.method == 'GET':
        return f"The URL /data is accessed directly. Try going to '/form' to submit form"

    if request.method == 'POST':
        if request.form['submit_button'] == 'Shoot':
            global missing_values
            missing_values =list() 
            speed_valid =1
            angle_valid =1
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
                    
            if missing_values:
                feedback = f"Missing fields for {', '.join(missing_values)}"
                return render_template('manuell.html',feedback=feedback)
            if not speed_valid:
                feedback = "Enter a valid speed within range 0-27 m/s"
                return render_template('manuell.html',feedback=feedback)
            if not angle_valid:
                feedback = "Enter a valid angle within range 5-45 degrees"
                return render_template('manuell.html',feedback=feedback)
            else:
                dict["Speed"]=int(request.form["speed"])
                dict["Angle"]=int(request.form["angle"])
                # fm.set_angle(int(request.form['angle']))
                # fm.set_speed(int(request.form['speed']))
                # fm.check_encoders(7*int(request.form["number_of_ballshots"]))
                # fm.set_speed(0)
                return render_template('data.html',form= dict)


        if request.form['submit_button'] == 'Shoot landingball':
            # fm.set_angle(int(request.form['angle']))
            # fm.set_speed(int(request.form['speed']))
            # fm.check_encoders(int(request.form['seconds']))
            # fm.set_speed(0)
            # form_data = request.form.copy()
            # form_data.add('expected encoder speed', set_speed)
            # form_data.add('motor lowest speed M1', minM1)
            # form_data.add('motor lowest speed M2', minM2)
            #return render_template('data.html',form= form_data)
            return render_template('data.html',form= request.form)

        if request.form['submit_button'] == 'submit':
            
            # fm.set_angle(int(request.form['angle']))
            # fm.set_speed(int(request.form['speed']))
            # fm.check_encoders(10)
            # fm.set_speed(0)
            return render_template('data.html',form= request.form)

@app.route('/calibrationdone', methods = ['POST', 'GET'])
def calibrationdone():        
    if request.method == 'GET':
        return f"The URL /data is accessed directly. Try going to '/form' to submit form"
    if request.method == 'POST':
        if request.form['submit_button'] == 'Calibrate':
            global dict
            dict['Landingspunkt']="{},{}".format(request.form["X"],request.form["Y"])
            #get real speed(landing, speed, angle) 
            #calibM1,calibM2
            #vis calibration.done
            return render_template('calibrationdone.html',form= dict)
 
@app.route('/calibrate', methods = ['POST', 'GET'])
def calibrate(): 
    if request.method == 'GET':
        return render_template('calibration.html')
    if request.method == 'POST':
        if request.form['submit_button'] == 'test_shot':
            # fm.set_angle(int(request.form['angle']))
            # fm.set_speed(int(request.form['speed']))
            # fm.check_encoders(10)
            # fm.set_speed(0)
            return render_template('calibration.html')


@app.route('/manuell')
def manuell():
    if request.method == 'GET':
        return render_template('manuell.html')
@app.route('/landing')
def landing():
    if request.method == 'GET':
        return render_template('landingspunkt.html')
@app.route('/keeper')
def keeper():
    if request.method == 'GET':
        return render_template('keeper.html')
@app.route('/calib1')
def calib1():
    if request.method == 'GET':
        global dict
        dict = {}
        return render_template('calib1.html')

@app.route('/calib2',methods = ['POST', 'GET'])
def calib2():
    if request.method == 'GET':
        return f"The URL /data is accessed directly. Try going to '/form' to submit form"
    if request.method == 'POST':   
        global missing_values
        missing_values =list() 
        speed_valid =1
        angle_valid =1
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
                
        if missing_values:
            feedback = f"Missing fields for {', '.join(missing_values)}"
            return render_template('calib1.html',feedback=feedback)
        if not speed_valid:
            feedback = "Enter a valid speed within range 0-27 m/s"
            return render_template('calib1.html',feedback=feedback)
        if not angle_valid:
            feedback = "Enter a valid angle within range 5-45 degrees"
            return render_template('calib1.html',feedback=feedback)
        else:
            dict["Speed"]=int(request.form["speed"])
            dict["Angle"]=int(request.form["angle"])
            # fm.set_angle(int(request.form['angle']))
            # fm.set_speed(int(request.form['speed']))
            # fm.check_encoders(10)
            # fm.set_speed(0)
            return render_template('calib2.html')

def valid_speed(speed):
    return (speed>=0 and speed<=27) 
    
def valid_angle(angle):
    return (angle>=0 and angle<=45)

if __name__ == '__main__':
 app.run(debug=False, host='0.0.0.0') 
