# Import the dependencies.
import sqlalchemy
import numpy as np
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from datetime import datetime as dt, timedelta

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///SurfsUp/Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

print(Base.classes.keys())
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB


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
        f"/api/v1.0/2015-02-12<br/>"
        f"/api/v1.0/2015-02-12/2017-02-12<br/>"
    )

@app.route("/api/v1.0/precipitation")
def prcp():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Find the most recent date in the data set.
    max_date = session.query(func.max(Measurement.date)).scalar()
    max_date_obj= dt.strptime(max_date, '%Y-%m-%d')


    # Calculate the date one year from the last date in data set.
    start_date_obj = session.query(func.date(max_date_obj, '-1 year')).scalar()

    # Perform a query to retrieve the data and precipitation scores
    query = session.query(Measurement.date, Measurement.prcp) \
    .filter(Measurement.date >= start_date_obj) \
    .filter(Measurement.date <= max_date_obj)
    results = query.all()
    session.close()

    # Convert list of tuples into normal list
    prcp = list(np.ravel(results))

    # return jsonify(prcp)
    prcp_last = []
    for date, p in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["precipitation"] = prcp
        
        prcp_last.append(prcp_dict)

    return jsonify(prcp_last)

@app.route("/api/v1.0/stations")
def stations():
    #Return a JSON list of stations from the dataset
    session = Session(engine)
    stations = session.query(Station.station).all()
    station_list = list(np.ravel(stations))
    return jsonify(station_list)
    session.close()
@app.route("/api/v1.0/tobs")
def tobs():
    #Query the dates and temperature observations of the most-active station for 
    #the previous year of data
    session = Session(engine)
    max_date = session.query(func.max(Measurement.date)).scalar()
    max_date_obj= dt.strptime(max_date, '%Y-%m-%d')
    start_date_obj = session.query(func.date(max_date_obj, '-1 year')).scalar()
    result = session.query((Measurement.date),(Measurement.tobs)) \
                .filter(Measurement.station == "USC00519281") \
                .filter(Measurement.date >= start_date_obj) \
                .filter(Measurement.date <= max_date_obj).all()
    session.close()
    temp_list = list(np.ravel(result))
    return jsonify(temp_list)
    
    
@app.route("/api/v1.0/<start>")
def from_start(start):
    session = Session(engine)
    result = session.query(func.min(Measurement.tobs),
                          func.max(Measurement.tobs),
                          func.avg(Measurement.tobs)) \
                .filter(Measurement.date >= start) \
                .all()
    session.close()
    
   
    temp_dict = {}
    temp_dict["min"] = result[0][0]
    temp_dict["max"] = result[0][1]
    temp_dict["avg"] = result[0][2]
    
    

    return jsonify(temp_dict)
    
@app.route("/api/v1.0/<start>/<end>")
def from_start_end(start,end):
    session = Session(engine)
    result = session.query(func.min(Measurement.tobs),
                          func.max(Measurement.tobs),
                          func.avg(Measurement.tobs)) \
                .filter(Measurement.date >= start) \
                .filter(Measurement.date <= end) \
                .all()
    session.close()
    
   
    temp_dict_end = {}
    temp_dict_end["min"] = result[0][0]
    temp_dict_end["max"] = result[0][1]
    temp_dict_end["avg"] = result[0][2]
    
    

    return jsonify(temp_dict_end)

if __name__ == "__main__":
    app.run(debug=True)
