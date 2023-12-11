# Import the dependencies.
import datetime as dt
from datetime import date

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

# Home Route
@app.route("/")
def home():
    """List all available API routes"""
    return (
        f"Welcome to my climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date<br/>"
        f"For start/end dates use YYYY-MM-DD format"
    )

# Precipitation Route
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the precipitation data as json"""
    # Create session link
    session = Session(engine)

    prev_year = dt.datetime(2017, 8, 23) - dt.timedelta(days=365)

    precip_scores = session.query(Measurement.date, Measurement.prcp).\
                filter(Measurement.date > prev_year).order_by(Measurement.date).all()
    
    # Close session
    session.close()

    precip_data = []
    for date, prcp in precip_scores:
        precip_dict = {}
        precip_dict['date'] = date
        precip_dict['precipitation'] = prcp
        precip_data.append(precip_dict)

    return jsonify(precip_data)

# Stations Route
@app.route("/api/v1.0/stations")
def get_stations():
    session = Session(engine)

    query = session.query(Station.station, Station.name).all()

    session.close()

    query_data = []
    for row in query:
        query_data.append({
            'station': row.station,
            'name': row.name
        }
        )

    return jsonify(query_data)

# Tobs Route
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    prev_year = dt.datetime(2017, 8, 23) - dt.timedelta(days=365)

    query = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.station == 'USC00519281', Measurement.date > prev_year).all()

    session.close()

    query_data = []
    for row in query:
        query_data.append({
            'date': row.date,
            'temp': row.tobs
        }
        )

    return jsonify(query_data)

# Specific Start Date Route
@app.route("/api/v1.0/<start>")
def start_date(start):
    session = Session(engine)

    start_date = date.fromisoformat(start)

    query = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
    filter(Measurement.date >= start_date).all()

    session.close()

    temp_data = []
    for min, max, avg in query:
        temp_dict = {}
        temp_dict['min'] = min
        temp_dict['max'] = max
        temp_dict['avg'] = avg
        temp_data.append(temp_dict)

    return jsonify(temp_data)

# Specific Start and End Date Route
@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    session = Session(engine)

    start_date = date.fromisoformat(start)
    end_date = date.fromisoformat(end)

    query = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
    filter(Measurement.date >= start_date, Measurement.date <= end_date).all()

    session.close()

    temp_data = []
    for min, max, avg in query:
        temp_dict = {}
        temp_dict['min'] = min
        temp_dict['max'] = max
        temp_dict['avg'] = avg
        temp_data.append(temp_dict)

    return jsonify(temp_data)

if __name__ == "__main__":
    app.run(debug=True)
