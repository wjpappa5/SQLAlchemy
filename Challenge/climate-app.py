import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False})


Bass = automap_base()
Bass.prepare(engine, reflect=True)
Bass.classes.keys()

prcpMeasurement = Bass.classes.measurement
ActiveStation = Bass.classes.station

engsession = Session(engine)

#weather app
app = Flask(__name__)


latest = (session.query(prcpMeasurement.date)
                .order_by(prcpMeasurement.date.desc())
                .first())
latest = list(np.ravel(latest))[0]

latest = dt.datetime.strptime(latest, '%Y-%m-%d')
Year = int(dt.datetime.strftime(latest, '%Y'))
Month = int(dt.datetime.strftime(latest, '%m'))
Day = int(dt.datetime.strftime(latest, '%d'))

yearprochaine = dt.date(Year, Month, Day) - dt.timedelta(days=365)
yearprochaine = dt.datetime.strftime(yearprochaine, '%Y-%m-%d')




@app.route("/")
def home():
    return (f"Welcome to Surf's Up!: Hawai'i Climate API<br/>"
            f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~<br/>"
            f"Available Routes:<br/>"
            f"/api/v1.0/stations ~~~~~ a list of all weather observation stations<br/>"
            f"/api/v1.0/precipitaton ~~ the latest year of precipitation data<br/>"
            f"/api/v1.0/temperature ~~ the latest year of temperature data<br/>"
            f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~<br/>"
            f"~~~ datesearch (yyyy-mm-dd)<br/>"
            f"/api/v1.0/datesearch/2012-12-21  ~~~~~~~~~~~ low, high, and average temp for date given and each date after<br/>"
            f"/api/v1.0/datesearch/2012-12-21/2012-12-31 ~~ low, high, and average temp for date given and each date up to and including end date<br/>"
            f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~<br/>"
            f"~ data available from 2010-01-01 to 2017-08-23 ~<br/>"
            f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

@app.route("/api/v1.0/stations")
def stations():
    results = engsession.query(ActiveStation.name).all()
    all_stations = list(np.ravel(results))
    return jsonify(all_stations)

@app.route("/api/v1.0/precipitaton")
def precipitation():
    
    results = (engsession.query(prcpMeasurement.date, prcpMeasurement.prcp, prcpMeasurement.station)
                      .filter(prcpMeasurement.date > yearprochaine)
                      .order_by(prcpMeasurement.date)
                      .all())
    
    precipraw = []
    for result in results:
        precipdic = {result.date: result.prcp, "Station": result.station}
        precipraw.append(precipdic)

    return jsonify(precipraw)

@app.route("/api/v1.0/temperature")
def temperature():

    results = (engsession.query(prcpMeasurement.date, prcpMeasurement.tobs, prcpMeasurement.station)
                      .filter(prcpMeasurement.date > yearprochaine)
                      .order_by(prcpMeasurement.date)
                      .all())

    tempraw = []
    for result in results:
        tempdic = {result.date: result.tobs, "Station": result.station}
        tempraw.append(tempdic)

    return jsonify(tempraw)

@app.route('/api/v1.0/datesearch/<startd>')
def start(startd):
    sel = [prcpMeasurement.date, func.min(prcpMeasurement.tobs), func.avg(prcpMeasurement.tobs), func.max(prcpMeasurement.tobs)]

    results =  (engsession.query(*sel)
                       .filter(func.strftime("%Y-%m-%d", prcpMeasurement.date) >= startd)
                       .group_by(prcpMeasurement.date)
                       .all())

    dates = []                       
    for result in results:
        date_dic = {}
        date_dic["Date"] = result[0]
        date_dic["Low Temp"] = result[1]
        date_dic["Avg Temp"] = result[2]
        date_dic["High Temp"] = result[3]
        dates.append(date_dic)
    return jsonify(dates)

@app.route('/api/v1.0/datesearch/<startd>/<endd>')
def startEnd(startd, endd):
    sel = [prcpMeasurement.date, func.min(prcpMeasurement.tobs), func.avg(prcpMeasurement.tobs), func.max(prcpMeasurement.tobs)]

    results =  (engsession.query(*sel)
                       .filter(func.strftime("%Y-%m-%d", prcpMeasurement.date) >= startd)
                       .filter(func.strftime("%Y-%m-%d", prcpMeasurement.date) <= endd)
                       .group_by(prcpMeasurement.date)
                       .all())

    dates = []                       
    for result in results:
        date_dic = {}
        date_dic["Date"] = result[0]
        date_dic["Low Temp"] = result[1]
        date_dic["Avg Temp"] = result[2]
        date_dic["High Temp"] = result[3]
        dates.append(date_dic)
    return jsonify(dates)

if __name__ == "__main__":
    app.run(debug=True)