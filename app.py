#!/usr/bin/env python3

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import numpy as np
import pandas as pd
import datetime as dt

from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt
from statistics import mean
import math

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station


#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
	"""List all available api routes."""
	return (
		f"Available Routes:<br/>"
		f"/api/v1.0/precipitation<br/>"
		f"/api/v1.0/stations<br/>"
		f"/api/v1.0/tobs<br/>"
		f"/api/v1.0/<start><br/>"
		f"/api/v1.0/<start>/<end><br/>"
	)
	
@app.route("/api/v1.0/precipitation")
def precipitation():
	# Create our session (link) from Python to the DB
	session = Session(engine)
	
	"""Return a list of all passenger names"""
	# Query all passengers
	results = session.query(Measurement.date, Measurement.prcp).order_by(Measurement.date.desc()).all()
	
	session.close()
	
	# Convert list of tuples into dictionary 
	dict = {a:b for (a,b) in results}
	
	return jsonify(dict)

@app.route("/api/v1.0/stations")
def stations():
	
	# Create our session (link) from Python to the DB
	session = Session(engine)
	
	"""Return a list of all stations"""
		#results = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).order_by(Measurement.station).all()
	results = session.query(Station.station, Station.name).group_by(Station.station).order_by(Station.station).all()
	
	
	session.close()
	
	# Convert list of tuples into dictionary 
	stations = {a:b for (a,b) in results}
	
	return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
	# Create our session (link) from Python to the DB
	session = Session(engine)
	
	"""Return a list of """
	
	sqlStr = "Select m.station, s.name, count(m.prcp) as stationCount "
	sqlStr += "FROM measurement as m "
	sqlStr += "left Join station as s on m.station = s.station "
	sqlStr += "Group by s.station "
	sqlStr += "order by stationCount desc"
	
	df = pd.read_sql_query( sqlStr, engine)
	
	mostActive = df.iloc[0,0]
	actName = df.iloc[0,1]
	
		
	results = session.query(Measurement.date, Measurement.tobs).order_by(Measurement.date.desc()).first()
	
	lastDateStr = results[0]
	print(lastDateStr)
	lastDate = dt.datetime.strptime(lastDateStr,"%Y-%m-%d")
	firstDate = lastDate - dt.timedelta(days=365.25)
	firstDateStr = firstDate.strftime('%Y-%m-%d')
	print(f"{firstDateStr} to {lastDateStr}")
	
	
	results = session.query( Measurement.date, func.avg(Measurement.tobs)).group_by(Measurement.date).filter(Measurement.date > firstDateStr).filter(Measurement.station == mostActive).order_by(Measurement.date).all()
	df = pd.DataFrame(results,columns=["Date", "Temperature"])
	
	df.replace([None],[0.0])
	df.fillna(0)
	df.dropna(how='any')
	df.Date = [dt.datetime.strptime(d,"%Y-%m-%d") for d in df.Date]
	
	df_1year = df[df.Date > firstDate]
	
		
	session.close()
	
	# Convert list of tuples into normal list
	#temps = {a:b for (a,b) in df_1year}
	
	return df_1year.to_json(orient='split')

# +++++++++++++++++++++++++++++++++++++++++++++++++





@app.route("/api/v1.0/<startDateStr>")
def stats1(startDateStr):
	
	start_date = dt.datetime.strptime(startDateStr,"%Y-%m-%d")	
	
	
	# Create our session (link) from Python to the DB
	session = Session(engine)
	
	"""Return a list of all passenger names"""
	# Query all passengers
	results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
	filter(Measurement.date >= start_date).all()	
	(min_temp, ave_temp, max_temp) = results[0]
	
	session.close()
	
	# Convert list of tuples into normal list
	stats = {"min_temp": min_temp, "ave_temp": ave_temp, "max_temp":max_temp}
	
	return jsonify(stats)

@app.route("/api/v1.0/<startDateStr>/<endDateStr>")
def stats2(startDateStr,endDateStr):
	
	start_date = dt.datetime.strptime(startDateStr,"%Y-%m-%d")	
	end_date = dt.datetime.strptime(endDateStr,"%Y-%m-%d")	
	
	# Create our session (link) from Python to the DB
	session = Session(engine)
	
	"""Return a list of all passenger names"""
	# Query all passengers
	results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
	filter(Measurement.date >= start_date).filter(Measurement.date < end_date).all()	
	
	
	(min_temp, ave_temp, max_temp) = list(np.ravel(results))
	
	session.close()
	
	# Convert list of tuples into normal list
	stats = {"min_temp": min_temp, "ave_temp": ave_temp, "max_temp":max_temp}
	
	return jsonify(stats)

		
if __name__ == '__main__':
	app.run(debug=True)
	