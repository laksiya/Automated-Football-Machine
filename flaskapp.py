# Flask on Apache
# https://asdkazmi.medium.com/deploying-flask-app-with-wsgi-and-apache-server-on-ubuntu-20-04-396607e0e40f
# To get access to html folder: sudo chown (check out raspberrys how to apache site)
import serial
from flask import Flask, render_template, request
from control_code import Footballmachine
from datetime import datetime
#port = serial.Serial(port="/dev/ttyS0", baudrate=38400, timeout=1, interCharTimeout=0.01)
#fm = Footballmachine()

app = Flask(__name__)
@app.errorhandler(500)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('500.html'), 500

app.register_error_handler(500, page_not_found)

@app.route('/')
def index():
    #fm.init_motors()
    return render_template('index.html')

@app.route('/manuell')
def manuell():
    #fm.init_motors()
    return render_template('manuell.html')

@app.route('/keeper')
def keeper():
    time = datetime.now()
    return render_template('keeper.html', time=time)

@app.route('/data', methods = ['POST', 'GET'])
def data():
    print(request.form['speed'])
    print(request.form['angle'])
    if request.method == 'GET':
        return f"The URL /data is accessed directly. Try going to '/form' to submit form"
    if request.method == 'POST':
        # fm.set_angle(int(request.form['angle']))
        # fm.set_speed(int(request.form['speed']))
        # fm.check_encoders(int(request.form['seconds']))
        # fm.set_speed(0)
        form_data = request.form
        return render_template('data.html',form= form_data)

if __name__ == '__main__':
 app.run(debug=False, host='0.0.0.0') 
