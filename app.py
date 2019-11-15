# 1. Import Dependencies
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False})

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# We can view all of the classes that automap found
Base.classes.keys()

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# # Create our session (link) from Python to the DB
session = Session(engine)

# 2. Create an app
app = Flask(__name__)

# 3. Define static routes
@app.route("/")
def index():
    return (
        f"Available Routes:<br/><br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start (enter in start date in the following format: YYYY-MM-DD)<br/>"
        f"/api/v1.0/start/end (enter in start and end dates in the following format: YYYY-MM-DD)<br/>"
    )

@app.route("/api/v1.0/precipitation")
# Convert the query results to a Dictionary using date as the key and prcp as the value.
# Return the JSON representation of your dictionary.
def precipitation():
    latest_date=session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    latest_date = pd.to_datetime(latest_date, format='%Y-%m-%d', errors='ignore')
    year_ago = latest_date-dt.timedelta(days = 365)
    year_ago = year_ago.strftime('%Y-%m-%d')
    rain = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date > year_ago[0]).\
        order_by(Measurement.date).all()

    return jsonify(rain)

@app.route("/api/v1.0/stations")
# Return a JSON list of stations from the dataset

def stations():
    all_station_query = session.query(Station.station)
    all_stations =[]
    for row in all_station_query:
        all_stations.append(row)
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
#Query for the dates and temperature observations from a year from the last data point.
#Return a JSON list of Temperature Observations (tobs) for the previous year.
def tobs():
    latest_date=session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    latest_date = pd.to_datetime(latest_date, format='%Y-%m-%d', errors='ignore')
    year_ago = latest_date-dt.timedelta(days = 365)
    year_ago = year_ago.strftime('%Y-%m-%d')
    temp = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date > year_ago[0]).\
        order_by(Measurement.date).all()

    return jsonify(temp)

@app.route("/api/v1.0/<start>")
# #Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# #When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
def greaterthanstart(start):
    greaterthan = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
    return jsonify(greaterthan)

@app.route("/api/v1.0/<start>/<end>")
#When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
def starttoend(start, end):
    startend = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start, Measurement.date <= end).all()
    return jsonify(startend)

if __name__ == "__main__":
    app.run(debug=True)


    