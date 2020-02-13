import json
import pytz
import datetime
import RPi.GPIO as GPIO
from flask import Flask, render_template, request, flash, url_for, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sensofdata.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

relay1 = 18
relay2 = 23

GPIO.setup(relay1, GPIO.OUT)
GPIO.setup(relay2, GPIO.OUT)

class autosensors(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    datentime = db.Column(db.DateTime, default=datetime.datetime.now(pytz.timezone("Asia/Calcutta")))
    ph = db.Column(db.Float, nullable=True, default=0.00)
    water_temp = db.Column(db.Float, nullable=True, default=0.00)
    humidity = db.Column(db.Float, nullable=True, default=0.00)
    room_temp = db.Column(db.Float, nullable=True, default=0.00)

class manualobservations(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    datentime = db.Column(db.DateTime, default=datetime.datetime.now(pytz.timezone("Asia/Calcutta")))
    ph_observation = db.Column(db.Float, nullable=True, default=0.00)
    ec_observation = db.Column(db.Float, nullable=True, default=0.00)
    tds_observation = db.Column(db.Float, nullable=True, default=0.00)
    plants_height = db.Column(db.Float, nullable=True, default=0.00)
    temperature = db.Column(db.Float, nullable=True, default=0.00)

@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    autodata = autosensors.query.all()
    autodata.reverse()
    autodata = autodata[:1]
    ph_dash = autodata[0].ph
    water_dash = autodata[0].water_temp
    humid_dash = autodata[0].humidity
    room_dash = autodata[0].room_temp
    swth = None
    stateofswitch = None
    switchvalue = None
    with open('switchdata.json') as f:
        data = json.load(f)
        print(data['switch'])
        cond = data['switch']
        if cond == 'on':
            stateofswitch = 'checked'
            switchvalue = 'on'
        else:
            stateofswitch = ''
            switchvalue = 'off'
        if request.method == 'POST':
            swth = request.json['swti']
            print(swth)
            if swth == 'on':
                GPIO.output(relay1, GPIO.LOW)
                GPIO.output(relay2, GPIO.HIGH)
                data = {'switch':'on'}
                with open('switchdata.json','w') as f:
                    json.dump(data, f)
            if swth == 'off':
                GPIO.output(relay1, GPIO.HIGH)
                GPIO.output(relay2, GPIO.LOW)
                data = {'switch':'off'}
                with open('switchdata.json','w') as f:
                    json.dump(data, f)
            return redirect(url_for('index'))
        return render_template('index.html',stateofswt=stateofswitch,swtvalue=switchvalue,ph_dash=ph_dash,water_dash=water_dash,humid_dash=humid_dash,room_dash=room_dash)

@app.route('/dataintable')
def showdata():
	autodata = autosensors.query.all()
	autodata.reverse()
	autodata = autodata[:10]
	manualdata = manualobservations.query.all()
	manualdata.reverse()
	manualdata = manualdata[:10]
	return render_template('tables.html',dataut=autodata,data=manualdata)

@app.route('/recorddata', methods=['GET', 'POST'])
def observations():
	if request.method == 'POST':
		ph = request.form['ph']
		ec = request.form['ec']
		tds = request.form['tds']
		plantht = request.form['plantht']
		tempinc = request.form['tempinc']
		new_data = manualobservations(ph_observation=float(ph),ec_observation=float(ec),tds_observation=float(tds),plants_height=float(plantht),temperature=float(tempinc))
		db.session.add(new_data)
		db.session.commit()
		manualdata = manualobservations.query.all()
		return redirect(url_for('showdata'))
	return render_template('recordobservation.html')

if __name__ == '__main__':
	app.run(host='0.0.0.0',port=5050,debug=True)
