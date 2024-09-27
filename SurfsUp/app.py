# Import the dependencies.
import numpy as np
import sqlalchemy
import datetime as dt

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask,jsonify

##########################################################
# Database setup
##########################################################
# create engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# View all of the classes that automap found
print(Base.classes.keys())

# Save references to each table
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
def home():
    """List all available routes."""
    return (
           f"&emsp;Available Routes:<br/>"
           f"&emsp;&emsp;1. /api/v1.0/precipitation<br/>"
           f"&emsp;&emsp;2. /api/v1.0/stations<br/>"
           f"&emsp;&emsp;3. /api/v1.0/tobs<br/>"
           f"&emsp;&emsp;4. /api/v1.0/start<br/>"
           f"&emsp;&emsp;5. /api/v1.0/start/end<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    max_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    max_date = max_date[0]
    max_day = int(max_date[-2:])
    max_year= int(max_date[:4])
    max_month = int(max_date[5:7])
    previous_year = dt.date(max_year,max_month,max_day)-dt.timedelta(days=365)

    prec_query = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= previous_year).order_by(Measurement.date).all()

    session.close()

    all_precipitation = []
    for date,prcp in prec_query:
        prec_dict = {}
        prec_dict[date] = prcp
        all_precipitation.append(prec_dict)

    return jsonify(all_precipitation)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    station_query = session.query(Station.id, Station.station, Station.name).\
    all()

    session.close()

    all_stations = []
    for id, station, name in station_query:
        station_dict = {}
        station_dict[id] = [station, name]
        all_stations.append(station_dict)

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    max_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    max_date = max_date[0]
    max_day = int(max_date[-2:])
    max_year= int(max_date[:4])
    max_month = int(max_date[5:7])
    previous_year = dt.date(max_year,max_month,max_day)-dt.timedelta(days=365)

    tobs_query = session.query(Station.name, Measurement.date, Measurement.tobs).\
    filter(Station.station == Measurement.station,Station.id == '7', Measurement.date >= previous_year).all()

    session.close()

    all_tobs = []
    for date,name,tobs in tobs_query:
        tobs_dict = {}
        tobs_dict[name] = [date,tobs]
        all_tobs.append(tobs_dict)

    return jsonify(all_tobs)

@app.route("/api/v1.0/<start>")
def startdate(start = ""):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    selection = [func.min(Measurement.tobs), func.avg(Measurement.tobs),func.max(Measurement.tobs)]
    start = dt.datetime.strptime(start,"%m%d%Y")
    results = session.query(*selection).filter(Measurement.date >= start).all()

    return jsonify(list(np.ravel(results)))

    session.close()

@app.route("/api/v1.0/<start>/<end>")
def start_and_end(start = "", end  = ""):

    session = Session(engine)

    selection = [func.min(Measurement.tobs), func.avg(Measurement.tobs),func.max(Measurement.tobs)]
    start = dt.datetime.strptime(start,"%m%d%Y")
    end = dt.datetime.strptime(end,"%m%d%Y")
    results = session.query(*selection).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    return jsonify(list(np.ravel(results)))

    session.close()

if __name__ == '__main__':
    app.run(debug=True)
