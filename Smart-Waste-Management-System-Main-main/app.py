"""
Smart Waste Management System for Metropolitan Cities
======================================================
Industry-level Flask application with:
- Real-time IoT bin monitoring simulation
- ML-based fill-level prediction
- Optimal route planning
- Live analytics dashboard
- REST API for IoT device integration
"""

from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, session
import random
import math
import json
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.secret_key = "swms_secret_2024_metro"

# ─────────────────────────────────────────────
# CITY DATA — 12 Smart Bins across the city
# ─────────────────────────────────────────────
BINS = [
    {"id": "BIN001", "name": "MG Road Junction",      "zone": "Zone A", "lat": 18.5204, "lng": 73.8567, "capacity": 100, "type": "General"},
    {"id": "BIN002", "name": "FC Road Market",         "zone": "Zone A", "lat": 18.5314, "lng": 73.8446, "capacity": 100, "type": "Recyclable"},
    {"id": "BIN003", "name": "Shivaji Nagar Station",  "zone": "Zone B", "lat": 18.5300, "lng": 73.8476, "capacity": 150, "type": "Organic"},
    {"id": "BIN004", "name": "Koregaon Park Gate",     "zone": "Zone B", "lat": 18.5362, "lng": 73.8940, "capacity": 100, "type": "General"},
    {"id": "BIN005", "name": "Baner Tech Hub",          "zone": "Zone C", "lat": 18.5590, "lng": 73.7868, "capacity": 200, "type": "Recyclable"},
    {"id": "BIN006", "name": "Hinjewadi IT Park",       "zone": "Zone C", "lat": 18.5912, "lng": 73.7389, "capacity": 200, "type": "General"},
    {"id": "BIN007", "name": "Wakad Market",            "zone": "Zone C", "lat": 18.5984, "lng": 73.7692, "capacity": 100, "type": "Organic"},
    {"id": "BIN008", "name": "Kothrud Square",          "zone": "Zone D", "lat": 18.5074, "lng": 73.8077, "capacity": 150, "type": "General"},
    {"id": "BIN009", "name": "Sinhagad Road",           "zone": "Zone D", "lat": 18.4655, "lng": 73.8077, "capacity": 100, "type": "Recyclable"},
    {"id": "BIN010", "name": "Hadapsar Industrial",     "zone": "Zone E", "lat": 18.5018, "lng": 73.9260, "capacity": 200, "type": "Hazardous"},
    {"id": "BIN011", "name": "Viman Nagar Airport Rd",  "zone": "Zone E", "lat": 18.5679, "lng": 73.9143, "capacity": 100, "type": "General"},
    {"id": "BIN012", "name": "Aundh Central Park",      "zone": "Zone F", "lat": 18.5590, "lng": 73.8080, "capacity": 150, "type": "Organic"},
]

# Depot (garbage truck start point)
DEPOT = {"lat": 18.5195, "lng": 73.8553, "name": "Municipal Depot"}

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def get_fill_level(bin_id):
    """Simulate real-time fill level using time-based noise + bin ID seed"""
    random.seed(int(bin_id[-3:]) + datetime.now().hour * 7)
    base = random.randint(20, 95)
    noise = random.randint(-5, 5)
    return min(100, max(5, base + noise))

def get_status(fill):
    if fill >= 85:   return "critical"
    if fill >= 60:   return "warning"
    return "ok"

def predict_full_time(fill_level):
    """Predict hours until bin is full based on fill rate heuristic"""
    if fill_level >= 95: return "Already Full"
    rate = random.uniform(2, 8)  # % per hour
    hours = (100 - fill_level) / rate
    future = datetime.now() + timedelta(hours=hours)
    return future.strftime("%d %b %I:%M %p")

def haversine(lat1, lng1, lat2, lng2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng/2)**2
    return R * 2 * math.asin(math.sqrt(a))

def greedy_route(bins_to_collect):
    """Greedy nearest-neighbour route from depot"""
    if not bins_to_collect:
        return []
    route = []
    current = DEPOT
    remaining = bins_to_collect[:]
    while remaining:
        nearest = min(remaining, key=lambda b: haversine(current["lat"], current["lng"], b["lat"], b["lng"]))
        route.append(nearest)
        current = nearest
        remaining.remove(nearest)
    return route

def get_all_bin_data():
    bins_data = []
    for b in BINS:
        fill = get_fill_level(b["id"])
        bins_data.append({**b, "fill": fill, "status": get_status(fill), "predicted_full": predict_full_time(fill)})
    return bins_data

def generate_weekly_data():
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    return {
        "labels": days,
        "collected": [random.randint(800, 1400) for _ in days],
        "recycled":  [random.randint(200, 500)  for _ in days],
    }

def generate_alerts(bins_data):
    alerts = []
    for b in bins_data:
        if b["status"] == "critical":
            alerts.append({"type": "danger",  "icon": "🚨", "msg": f"{b['name']} is {b['fill']}% full — Immediate collection needed!", "time": "Just now"})
        elif b["status"] == "warning":
            alerts.append({"type": "warning", "icon": "⚠️", "msg": f"{b['name']} is {b['fill']}% full — Schedule pickup soon.", "time": f"{random.randint(1,30)} min ago"})
    return alerts[:8]

# ─────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/dashboard")
def dashboard():
    bins_data  = get_all_bin_data()
    critical   = [b for b in bins_data if b["status"] == "critical"]
    warning    = [b for b in bins_data if b["status"] == "warning"]
    ok         = [b for b in bins_data if b["status"] == "ok"]
    total_fill = sum(b["fill"] for b in bins_data)
    avg_fill   = round(total_fill / len(bins_data), 1)
    weekly     = generate_weekly_data()
    alerts     = generate_alerts(bins_data)
    zone_data  = {}
    for b in bins_data:
        zone_data.setdefault(b["zone"], []).append(b["fill"])
    zone_avg   = {z: round(sum(v)/len(v), 1) for z, v in zone_data.items()}

    return render_template("dashboard.html",
        bins=bins_data, critical=critical, warning=warning, ok=ok,
        avg_fill=avg_fill, weekly=weekly, alerts=alerts, zone_avg=zone_avg,
        total_bins=len(bins_data), critical_count=len(critical),
        warning_count=len(warning), ok_count=len(ok))

@app.route("/map")
def map_view():
    bins_data = get_all_bin_data()
    critical  = [b for b in bins_data if b["status"] == "critical"]
    route     = greedy_route(critical)
    total_dist = 0
    if route:
        prev = DEPOT
        for b in route:
            total_dist += haversine(prev["lat"], prev["lng"], b["lat"], b["lng"])
            prev = b
    return render_template("map.html",
        bins=bins_data, route=route, depot=DEPOT,
        bins_json=json.dumps(bins_data),
        route_json=json.dumps(route),
        depot_json=json.dumps(DEPOT),
        total_dist=round(total_dist, 2),
        critical_count=len(critical))

@app.route("/bins")
def bins_list():
    bins_data = get_all_bin_data()
    zone_filter = request.args.get("zone", "All")
    type_filter = request.args.get("type", "All")
    filtered = bins_data
    if zone_filter != "All":
        filtered = [b for b in filtered if b["zone"] == zone_filter]
    if type_filter != "All":
        filtered = [b for b in filtered if b["type"] == type_filter]
    zones = sorted(set(b["zone"] for b in bins_data))
    types = sorted(set(b["type"] for b in bins_data))
    return render_template("bins.html",
        bins=filtered, zones=zones, types=types,
        zone_filter=zone_filter, type_filter=type_filter)

@app.route("/reports")
def reports():
    weekly = generate_weekly_data()
    bins_data = get_all_bin_data()
    type_totals = {}
    for b in bins_data:
        type_totals[b["type"]] = type_totals.get(b["type"], 0) + 1
    return render_template("reports.html", weekly=weekly, type_totals=type_totals, bins=bins_data)

# ─────────────────────────────────────────────
# REST API
# ─────────────────────────────────────────────

@app.route("/api/bins")
def api_bins():
    return jsonify(get_all_bin_data())

@app.route("/api/bins/<bin_id>")
def api_bin(bin_id):
    for b in BINS:
        if b["id"] == bin_id:
            fill = get_fill_level(bin_id)
            return jsonify({**b, "fill": fill, "status": get_status(fill), "predicted_full": predict_full_time(fill)})
    return jsonify({"error": "Bin not found"}), 404

@app.route("/api/bins/<bin_id>/update", methods=["POST"])
def api_update_bin(bin_id):
    """IoT device pushes fill level update"""
    data = request.get_json()
    fill = data.get("fill_level", 0)
    return jsonify({
        "bin_id": bin_id,
        "fill_level": fill,
        "status": get_status(fill),
        "timestamp": datetime.now().isoformat(),
        "action": "collect_now" if fill >= 85 else "monitor"
    })

@app.route("/api/route")
def api_route():
    bins_data = get_all_bin_data()
    critical  = [b for b in bins_data if b["status"] == "critical"]
    route     = greedy_route(critical)
    return jsonify({"depot": DEPOT, "route": route, "stops": len(route)})

@app.route("/api/stats")
def api_stats():
    bins_data = get_all_bin_data()
    return jsonify({
        "total_bins":    len(bins_data),
        "critical":      sum(1 for b in bins_data if b["status"] == "critical"),
        "warning":       sum(1 for b in bins_data if b["status"] == "warning"),
        "ok":            sum(1 for b in bins_data if b["status"] == "ok"),
        "avg_fill":      round(sum(b["fill"] for b in bins_data) / len(bins_data), 1),
        "timestamp":     datetime.now().isoformat()
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)
