# ♻️ Smart Waste Management System for Metropolitan Cities

> **Industry-level IoT + AI web platform for intelligent urban waste monitoring, alert management, and route optimization — built for Pune Metropolitan Region.**

---

## 🌟 Project Overview

The **Smart Waste Management System (SWMS)** is an advanced full-stack web application that simulates a real-world IoT-powered waste monitoring platform for metropolitan cities. It integrates real-time bin fill-level tracking, AI-based route optimization, live analytics, and a REST API for IoT device connectivity.

Built using **Python Flask**, **Leaflet.js maps**, **Chart.js analytics**, and a **professional dark-sidebar UI**, this project demonstrates an end-to-end smart city solution aligned with **UN SDG 11 (Sustainable Cities)**.

---

## 📁 Folder Structure

```
Smart-Waste-Management-System/
├── Documentation/
│   └── Project_Documentation.docx
├── static/
│   └── css/
│       └── style.css
├── templates/
│   ├── _sidebar.html          ← Shared sidebar component
│   ├── home.html              ← Landing page
│   ├── dashboard.html         ← Live analytics dashboard
│   ├── map.html               ← Interactive map + route
│   ├── bins.html              ← Bin monitoring grid
│   └── reports.html           ← Weekly analytics & KPIs
├── app.py                     ← Main Flask application
├── requirements.txt
└── README.md
```

---

## 🛠️ Technologies Used

| Layer            | Technology                                    |
|------------------|-----------------------------------------------|
| Backend          | Python 3, Flask 3.1                          |
| Frontend         | HTML5, CSS3 (custom dark-sidebar UI)          |
| Maps             | Leaflet.js + OpenStreetMap                   |
| Charts           | Chart.js (bar, doughnut, pie, line)          |
| Routing Algorithm| Greedy Nearest-Neighbour (Haversine distance) |
| IoT Simulation   | Time-seeded random fill-level generator       |
| API              | Flask REST API (JSON)                         |
| Version Control  | Git & GitHub                                  |

---

## 🏙️ System Architecture

```
IoT Sensors (Simulated)
        ↓
Flask Backend (app.py)
   ├── /dashboard  → Live stats, charts, alerts
   ├── /map        → Leaflet map + AI route
   ├── /bins       → Card-based bin grid
   ├── /reports    → Weekly KPI analytics
   └── /api/*      → REST endpoints for IoT/mobile
        ↓
Jinja2 Templates → HTML/CSS/JS → User Browser
```

---

## ✨ Features

### 📊 Live Dashboard
- 4 KPI stat cards: Total Bins, Critical, Warning, Avg Fill %
- Chart.js bar chart for weekly waste collection vs recycled
- Doughnut chart for bin status distribution
- Real-time alert feed with severity indicators
- Zone-wise average fill level grid

### 🗺️ Interactive Map
- Leaflet.js map with all 12 bin locations (Pune city)
- Color-coded markers: 🔴 Critical / 🟡 Warning / 🟢 OK
- **AI-optimized truck route** (Greedy Nearest-Neighbour algorithm)
- Animated route polyline with numbered stop markers
- Distance & estimated travel time calculation

### 🗑️ Bin Monitor
- Responsive card grid for all bins
- Filter by Zone and Waste Type
- Real-time fill bars, predicted full time
- Status badges (Critical / Warning / OK)

### 📈 Reports
- Weekly collection & recycling trends (line + bar charts)
- Waste type pie chart
- KPI metrics: Total collected, recycled, recycling rate
- Full bin status table

### 🔗 REST API
- `GET /api/bins` — All bin status
- `GET /api/bins/<id>` — Single bin details
- `POST /api/bins/<id>/update` — IoT device push
- `GET /api/route` — Optimized collection route
- `GET /api/stats` — City-level statistics

---

## 🚀 Setup & Run

### Step 1: Install dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run the app
```bash
python app.py
```

### Step 3: Open browser
```
http://localhost:5000
```

---

## 📡 IoT Sensor Simulation

Each bin has a **time-seeded fill level generator** that simulates ultrasonic distance sensor readings:

```python
def get_fill_level(bin_id):
    random.seed(int(bin_id[-3:]) + datetime.now().hour * 7)
    base = random.randint(20, 95)
    return min(100, max(5, base + noise))
```

This ensures fill levels are consistent within each hour (realistic IoT behavior) and change across hours (simulating actual waste accumulation).

---

## 🤖 Route Optimization Algorithm

The system uses a **Greedy Nearest-Neighbour** algorithm to compute optimal truck collection routes:

```python
def greedy_route(bins_to_collect):
    route = []
    current = DEPOT
    remaining = bins_to_collect[:]
    while remaining:
        nearest = min(remaining, key=lambda b: haversine(...))
        route.append(nearest)
        current = nearest
    return route
```

Distance is calculated using the **Haversine Formula** for accurate GPS-based distance computation.

---

## 🌍 SDG Alignment

| Goal | Description |
|------|-------------|
| SDG 11 | Sustainable Cities and Communities |
| SDG 12 | Responsible Consumption and Production |
| SDG 14 | Life Below Water (reduce landfill runoff) |
| SDG 15 | Life on Land (reduce plastic pollution) |

---

## 🔮 Future Enhancements

- Live integration with real ultrasonic sensors (Arduino/Raspberry Pi via MQTT)
- Machine learning model for fill-level forecasting (LSTM)
- Mobile app for sanitation workers (React Native)
- SMS/email alerts for municipal supervisors
- Database integration (PostgreSQL) for historical analytics
- Deployment on AWS EC2 with auto-scaling

---

## Project Screenshots

1 Home Page -
* <img width="960" height="441" alt="Screenshot 2026-06-23 131845" src="https://github.com/user-attachments/assets/bfd72393-6b8e-4553-acbb-b8a41e3b8696" />


2 Live Map Page -
* <img width="959" height="440" alt="image" src="https://github.com/user-attachments/assets/2a137322-804a-477c-a20b-75f6f4b238d6" />


3 Dashboard Page -
* <img width="960" height="437" alt="image" src="https://github.com/user-attachments/assets/c9475715-6c89-4783-aa8a-dbe0d5c559d3" />


4 Bin Moniter Page -
* <img width="960" height="449" alt="image" src="https://github.com/user-attachments/assets/3dd9ed9d-9f1b-4702-b501-84299abff3bb" />


5 Report Page -
* <img width="960" height="437" alt="image" src="https://github.com/user-attachments/assets/5c3c5c94-0792-45a4-a69c-8b3c520ccbb8" />


* <img width="960" height="438" alt="Screenshot 2026-06-23 132740" src="https://github.com/user-attachments/assets/1e405705-defd-4537-97ab-73d644d4408b" />


* <img width="960" height="433" alt="Screenshot 2026-06-23 132804" src="https://github.com/user-attachments/assets/06bebebf-ff01-4ad2-a969-ab9b18862c8b" />


Git Repo - https://github.com/Pruthviraj-01/Smart-Waste-Management-System-Main.git

Demo Video- https://drive.google.com/file/d/1OwLa97n2w0KFCPWFcfSKB_4p0ZOPHL4q/view?usp=sharing 

## 👤 Author

**Your Name**
Final Year Project — IoT / Smart Cities / Web Development
SmartInternz Externship Program — 2024
