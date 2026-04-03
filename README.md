# SkyBook, CS 6083 PS3 Q1 (Flask + SQLite)

A self-contained Flask web app. Uses **SQLite** (built into Python), no external database needed.

## Quick Start

```bash
# 1. Install Flask (the only dependency)
pip install flask

# 2. Run
python app.py

# 3. Open http://localhost:5000
```

The SQLite database (`airline.db`) is created automatically on first run, pre-loaded with
sample airports, aircraft, flights, passengers, and bookings.

---

## Demo Data

Try these routes with dates **2026-04-05 to 2026-04-10**:

| Route | Flights |
|-------|---------|
| JFK → LAX | AA101 |
| JFK → ORD | UA201 |
| JFK → LHR | BA301 |
| JFK → MIA | DL401 |
| JFK → CDG | AF501 |
| JFK → SFO | AA801 |
| SFO → ORD | UA601 |
| BOS → LAX | DL701 |

---

## Features

### Part (a), Search Form `/`
- Origin & destination airport code inputs
- Date range pickers (continuous range)
- Client + server-side validation

### Part (b), Flight Results `/flights` (POST)
SQL:
```sql
SELECT f.flight_number, f.departure_date, fs.airline_name,
       fs.origin_code, fs.dest_code, fs.departure_time, fs.duration
FROM Flight f
JOIN FlightService fs ON f.flight_number = fs.flight_number
WHERE fs.origin_code   = ?
  AND fs.dest_code     = ?
  AND f.departure_date BETWEEN ? AND ?
ORDER BY f.departure_date, fs.departure_time
```

### Part (c), Seat Availability `/flight/<number>/<date>`
SQL:
```sql
SELECT a.capacity,
       (a.capacity - COUNT(b.seat_number)) AS available_seats
FROM Flight f
JOIN FlightService fs ON f.flight_number  = fs.flight_number
JOIN Aircraft a       ON f.plane_type     = a.plane_type
LEFT JOIN Booking b   ON  b.flight_number  = f.flight_number
                      AND b.departure_date = f.departure_date
WHERE f.flight_number = ? AND f.departure_date = ?
GROUP BY a.capacity
```
Shows: available seats, total capacity, booked seats, visual occupancy bar, and color-coded status.

---

## Schema

```
Airport       (airport_code PK, name, city, country)
Aircraft      (plane_type PK, capacity)
FlightService (flight_number PK, airline_name, origin_code FK, dest_code FK, departure_time, duration)
Flight        (flight_number FK, departure_date) PK=(flight_number, departure_date)
Passenger     (pid PK, passenger_name)
Booking       (pid FK, flight_number FK, departure_date FK, seat_number)
              PK=(pid, flight_number, departure_date)
```
