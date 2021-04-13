# Flask on Apache
# https://asdkazmi.medium.com/deploying-flask-app-with-wsgi-and-apache-server-on-ubuntu-20-04-396607e0e40f
# To get access to html folder: sudo chown (check out raspberrys how to apache site)

from flask import Flask, render_template
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cakes/<name>')
def cakes(name):
    time = datetime.now()
    return render_template('cakes.html', name=name, time=time)

@app.route('/cakes')
def cakes_default():
    time = datetime.now()
    return render_template('cakes.html', name="", time=time)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')