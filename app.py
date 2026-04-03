import os
import psycopg2
import psycopg2.extras
from flask import Flask, render_template, request, g
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db():
    if "db" not in g:
        g.db = psycopg2.connect(DATABASE_URL)
        g.db.autocommit = False
    return g.db

@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db:
        db.close()

SCHEMA = """
CREATE TABLE IF NOT EXISTS Airport (
    airport_code TEXT PRIMARY KEY,
    name         TEXT NOT NULL,
    city         TEXT NOT NULL,
    country      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Aircraft (
    plane_type TEXT PRIMARY KEY,
    capacity   INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS FlightService (
    flight_number  TEXT    PRIMARY KEY,
    airline_name   TEXT    NOT NULL,
    origin_code    TEXT    NOT NULL REFERENCES Airport(airport_code),
    dest_code      TEXT    NOT NULL REFERENCES Airport(airport_code),
    departure_time TEXT    NOT NULL,
    duration       INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS Flight (
    flight_number  TEXT NOT NULL REFERENCES FlightService(flight_number),
    departure_date DATE NOT NULL,
    plane_type     TEXT NOT NULL REFERENCES Aircraft(plane_type),
    PRIMARY KEY (flight_number, departure_date)
);

CREATE TABLE IF NOT EXISTS Passenger (
    pid            SERIAL PRIMARY KEY,
    passenger_name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Booking (
    pid            INTEGER NOT NULL REFERENCES Passenger(pid),
    flight_number  TEXT    NOT NULL,
    departure_date DATE    NOT NULL,
    seat_number    INTEGER NOT NULL,
    PRIMARY KEY (pid, flight_number, departure_date),
    FOREIGN KEY (flight_number, departure_date)
        REFERENCES Flight(flight_number, departure_date)
);
"""

SEED = """
INSERT INTO Airport VALUES
('JFK', 'John F Kennedy International',     'New York',      'United States'),
('LAX', 'Los Angeles International',        'Los Angeles',   'United States'),
('ORD', 'O''Hare International',            'Chicago',       'United States'),
('LHR', 'Heathrow Airport',                 'London',        'United Kingdom'),
('CDG', 'Charles de Gaulle Airport',        'Paris',         'France'),
('SFO', 'San Francisco International',      'San Francisco', 'United States'),
('MIA', 'Miami International',              'Miami',         'United States'),
('ATL', 'Hartsfield-Jackson International', 'Atlanta',       'United States'),
('NRT', 'Narita International',             'Tokyo',         'Japan'),
('SIN', 'Changi Airport',                   'Singapore',     'Singapore')
ON CONFLICT DO NOTHING;

INSERT INTO Aircraft VALUES
('CRJ-200',    10),
('Boeing 737', 20),
('Airbus A320',15),
('Boeing 787', 25)
ON CONFLICT DO NOTHING;

INSERT INTO FlightService VALUES
('AA101', 'American Airlines',  'JFK', 'LAX', '08:00', 210),
('AA205', 'American Airlines',  'JFK', 'LAX', '14:00', 210),
('UA302', 'United Airlines',    'SFO', 'ORD', '09:00', 360),
('DL410', 'Delta Air Lines',    'ATL', 'MIA', '10:00', 150),
('BA178', 'British Airways',    'LHR', 'JFK', '10:00', 180),
('AF023', 'Air France',         'CDG', 'NRT', '22:00', 1140),
('SQ321', 'Singapore Airlines', 'SIN', 'LHR', '23:00', 420),
('AA550', 'American Airlines',  'ORD', 'MIA', '07:00', 240),
('DL620', 'Delta Air Lines',    'JFK', 'ATL', '16:00', 150),
('UA789', 'United Airlines',    'LAX', 'SFO', '12:00', 90)
ON CONFLICT DO NOTHING;

INSERT INTO Flight VALUES
('AA101', '2025-12-29', 'Boeing 737'),
('AA101', '2025-12-31', 'Boeing 737'),
('AA205', '2025-12-31', 'Boeing 737'),
('UA302', '2025-12-31', 'CRJ-200'),
('DL410', '2025-12-31', 'Airbus A320'),
('BA178', '2025-12-31', 'Boeing 787'),
('AF023', '2025-12-30', 'Boeing 787'),
('SQ321', '2025-12-30', 'Boeing 787'),
('DL620', '2025-12-30', 'Airbus A320'),
('DL620', '2025-12-31', 'Airbus A320'),
('AA550', '2025-12-31', 'CRJ-200'),
('UA789', '2025-12-31', 'Airbus A320')
ON CONFLICT DO NOTHING;

INSERT INTO Passenger (pid, passenger_name) OVERRIDING SYSTEM VALUE VALUES
(1,'John Adams'),(2,'Sarah Miller'),(3,'Michael Chen'),
(4,'Emily Wong'),(5,'David Park'),(6,'Lisa Johnson'),
(7,'James Brown'),(8,'Maria Garcia'),(9,'Robert Kim'),
(10,'Jennifer Lee'),(11,'Thomas Wilson'),(12,'Amanda Clark'),
(13,'Christopher Davis'),(14,'Jessica Martinez'),(15,'Daniel Taylor'),
(16,'Rachel Anderson'),(17,'William Thomas'),(18,'Nicole White'),
(19,'Kevin Harris'),(20,'Stephanie Moore'),(21,'Andrew Jackson'),
(22,'Michelle Robinson'),(23,'Brian Lewis'),(24,'Laura Walker'),
(25,'Steven Hall')
ON CONFLICT DO NOTHING;

INSERT INTO Booking VALUES
(1,'AA101','2025-12-29',1),(2,'AA101','2025-12-29',2),(3,'AA101','2025-12-29',3),
(4,'AA101','2025-12-29',4),(5,'AA101','2025-12-29',5),
(1,'AA101','2025-12-31',1),(2,'AA101','2025-12-31',2),(3,'AA101','2025-12-31',3),
(4,'AA101','2025-12-31',4),(5,'AA101','2025-12-31',5),(6,'AA101','2025-12-31',6),
(7,'AA101','2025-12-31',7),(8,'AA101','2025-12-31',8),(9,'AA101','2025-12-31',9),
(10,'AA101','2025-12-31',10),(11,'AA101','2025-12-31',11),(12,'AA101','2025-12-31',12),
(13,'AA101','2025-12-31',13),(14,'AA101','2025-12-31',14),(15,'AA101','2025-12-31',15),
(16,'AA205','2025-12-31',1),(17,'AA205','2025-12-31',2),
(18,'AA205','2025-12-31',3),(19,'AA205','2025-12-31',4),
(1,'UA302','2025-12-31',1),(2,'UA302','2025-12-31',2),(3,'UA302','2025-12-31',3),
(4,'UA302','2025-12-31',4),(5,'UA302','2025-12-31',5),(6,'UA302','2025-12-31',6),
(7,'UA302','2025-12-31',7),(8,'UA302','2025-12-31',8),(9,'UA302','2025-12-31',9),
(10,'UA302','2025-12-31',10),
(5,'DL410','2025-12-31',1),(6,'DL410','2025-12-31',2),(7,'DL410','2025-12-31',3),
(8,'DL410','2025-12-31',4),(9,'DL410','2025-12-31',5),(10,'DL410','2025-12-31',6),
(11,'DL410','2025-12-31',7),(12,'DL410','2025-12-31',8),(13,'DL410','2025-12-31',9),
(14,'DL410','2025-12-31',10),(15,'DL410','2025-12-31',11),(16,'DL410','2025-12-31',12),
(17,'DL410','2025-12-31',13),(18,'DL410','2025-12-31',14),
(20,'BA178','2025-12-31',1),(21,'BA178','2025-12-31',2),(22,'BA178','2025-12-31',3),
(23,'BA178','2025-12-31',4),(24,'BA178','2025-12-31',5),(25,'BA178','2025-12-31',6),
(1,'AF023','2025-12-30',1),(2,'AF023','2025-12-30',2),
(3,'AF023','2025-12-30',3),(4,'AF023','2025-12-30',4),
(5,'SQ321','2025-12-30',1),(6,'SQ321','2025-12-30',2),(7,'SQ321','2025-12-30',3),
(10,'DL620','2025-12-30',1),(11,'DL620','2025-12-30',2),
(12,'DL620','2025-12-30',3),(13,'DL620','2025-12-30',4),
(20,'DL620','2025-12-31',1),(21,'DL620','2025-12-31',2),(22,'DL620','2025-12-31',3),
(23,'DL620','2025-12-31',4),(24,'DL620','2025-12-31',5),
(8,'AA550','2025-12-31',1),(9,'AA550','2025-12-31',2),(10,'AA550','2025-12-31',3),
(11,'AA550','2025-12-31',4),(12,'AA550','2025-12-31',5),
(13,'AA550','2025-12-31',6),(14,'AA550','2025-12-31',7),
(22,'UA789','2025-12-31',1),(23,'UA789','2025-12-31',2),(24,'UA789','2025-12-31',3)
ON CONFLICT DO NOTHING;
"""

def init_db():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute(SCHEMA)
    cur.execute(SEED)
    conn.commit()
    cur.close()
    conn.close()

@app.route("/", methods=["GET"])
def index():
    db = get_db()
    cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT airport_code, name, city, country FROM Airport ORDER BY city, name")
    airports = cur.fetchall()
    cur.close()
    return render_template("index.html", airports=airports)


@app.route("/flights", methods=["POST"])
def flights():
    origin      = request.form.get("origin", "").strip().upper()
    destination = request.form.get("destination", "").strip().upper()
    start_date  = request.form.get("start_date", "").strip()
    end_date    = request.form.get("end_date", "").strip()

    errors = []
    if not origin:
        errors.append("Origin airport code is required.")
    if not destination:
        errors.append("Destination airport code is required.")
    if not start_date:
        errors.append("Start date is required.")
    if not end_date:
        errors.append("End date is required.")
    if start_date and end_date and start_date > end_date:
        errors.append("Start date must be on or before end date.")
    if origin and destination and origin == destination:
        errors.append("Origin and destination cannot be the same airport.")

    if errors:
        db = get_db()
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT airport_code, name, city, country FROM Airport ORDER BY city, name")
        airports = cur.fetchall()
        cur.close()
        return render_template("index.html", errors=errors,
                               origin=origin, destination=destination,
                               start_date=start_date, end_date=end_date,
                               airports=airports)

    sql = """
        SELECT
            f.flight_number,
            f.departure_date,
            fs.airline_name,
            fs.origin_code,
            fs.dest_code,
            fs.departure_time,
            fs.duration
        FROM Flight f
        JOIN FlightService fs ON f.flight_number = fs.flight_number
        WHERE fs.origin_code   = %s
          AND fs.dest_code     = %s
          AND f.departure_date BETWEEN %s AND %s
        ORDER BY f.departure_date, fs.departure_time
    """
    db  = get_db()
    cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(sql, (origin, destination, start_date, end_date))
    result = cur.fetchall()
    cur.close()

    return render_template("flights.html",
                           flights=result,
                           origin=origin,
                           destination=destination,
                           start_date=start_date,
                           end_date=end_date)


@app.route("/flight/<flight_number>/<departure_date>")
def flight_detail(flight_number, departure_date):
    sql = """
        SELECT
            f.flight_number,
            f.departure_date,
            fs.airline_name,
            fs.origin_code,
            fs.dest_code,
            fs.departure_time,
            fs.duration,
            f.plane_type,
            a.capacity,
            (a.capacity - COUNT(b.seat_number)) AS available_seats
        FROM Flight f
        JOIN FlightService fs ON f.flight_number  = fs.flight_number
        JOIN Aircraft a       ON f.plane_type     = a.plane_type
        LEFT JOIN Booking b   ON  b.flight_number  = f.flight_number
                              AND b.departure_date = f.departure_date
        WHERE f.flight_number  = %s
          AND f.departure_date = %s
        GROUP BY f.flight_number, f.departure_date,
                 fs.airline_name, fs.origin_code, fs.dest_code,
                 fs.departure_time, fs.duration, f.plane_type, a.capacity
    """
    db  = get_db()
    cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(sql, (flight_number, departure_date))
    flight = cur.fetchone()
    cur.close()

    if not flight:
        return render_template("error.html",
                               message=f"Flight {flight_number} on {departure_date} not found.")

    return render_template("flight_detail.html", flight=flight)


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)
