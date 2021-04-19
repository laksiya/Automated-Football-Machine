# Flask on Apache
# https://asdkazmi.medium.com/deploying-flask-app-with-wsgi-and-apache-server-on-ubuntu-20-04-396607e0e40f
# To get access to html folder: sudo chown (check out raspberrys how to apache site)

from flask import Flask, render_template, request
 
from datetime import datetime

app = Flask(__name__)
@app.errorhandler(500)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('500.html'), 500
app.register_error_handler(500, page_not_found)
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

@app.route('/data/', methods = ['POST', 'GET'])
def data():
    print(request.form['speed'])
    print(request.form['angle'])
    d = request.form.to_dict()
    print(d)
    if request.method == 'GET':
        return f"The URL /data is accessed directly. Try going to '/form' to submit form"
    if request.method == 'POST':
        form_data = request.form
        return render_template('data.html',form = form_data)

@app.errorhandler(500)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')