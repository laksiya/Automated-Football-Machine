# Flask on Apache
# https://asdkazmi.medium.com/deploying-flask-app-with-wsgi-and-apache-server-on-ubuntu-20-04-396607e0e40f
# To get access to html folder: sudo chown (check out raspberrys how to apache site)
import serial
from flask import Flask, render_template, request
from control_code import Footballmachine
from datetime import datetime
#port = serial.Serial(port="/dev/ttyS0", baudrate=38400, timeout=1, interCharTimeout=0.01)
fm = Footballmachine()

app = Flask(__name__)
@app.errorhandler(500)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('500.html'), 500

app.register_error_handler(500, page_not_found)


@app.route('/')
def index():
    if request.method == 'GET':
        #fm.init_motors()
        return render_template('main.html')

    if request.method == 'POST':
        if request.form['submit_button'] == 'test_shot':
            # fm.set_angle(int(request.form['angle']))
            # fm.set_speed(int(request.form['speed']))
            # fm.check_encoders(10)
            # fm.set_speed(0)
            return render_template('main.html')

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
        if request.form['submit_button'] == 'manuell':
            # fm.set_angle(int(request.form['angle']))
            # fm.set_speed(int(request.form['speed']))
            # fm.check_encoders(10)
            # fm.set_speed(0)
            return render_template('data.html',form= request.form)
        if request.form['submit_button'] == 'landing':
            # fm.set_angle(int(request.form['angle']))
            # fm.set_speed(int(request.form['speed']))
            # fm.check_encoders(int(request.form['seconds']))
            # fm.set_speed(0)
            #form_data = request.form.copy()
            # form_data.add('expected encoder speed', set_speed)
            # form_data.add('motor lowest speed M1', minM1)
            # form_data.add('motor lowest speed M2', minM2)
            #return render_template('data.html',form= form_data)
            return render_template('data.html',form= request.form)
        if request.form['submit_button'] == 'keeper':
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
        if request.form['submit_button'] == 'calibrate':
            #get real speed(landing, speed, angle) 
            #calibM1,calibM2
            #vis calibration.done
            return render_template('calibrationdone.html',form= request.form)
 
@app.route('/calibration', methods = ['POST', 'GET'])
def calibration(): 
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
if __name__ == '__main__':
 app.run(debug=False, host='0.0.0.0') 
