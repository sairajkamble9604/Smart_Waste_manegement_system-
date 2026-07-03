import json
import threading
import os
from datetime import datetime

DATA_FILE = os.path.join(os.path.dirname(__file__), "data.json")
_lock = threading.Lock()

_default_data = {
    "users": [
        {
            "id": 1,
            "name": "System Administrator",
            "email": "admin@bloodbridge.com",
            "password": "admin123",
            "role": "admin",
            "phone": "+1-555-0100",
            "city": "New York",
            "status": "active",
            "created_at": "2024-01-01",
        },
        {
            "id": 2,
            "name": "City General Hospital",
            "email": "citygen@hospital.com",
            "password": "admin123",
            "role": "hospital",
            "phone": "+1-555-0200",
            "address": "123 Health Ave",
            "city": "New York",
            "status": "active",
            "created_at": "2024-01-02",
        },
        {
            "id": 3,
            "name": "St. Mary Medical Center",
            "email": "stmary@hospital.com",
            "password": "admin123",
            "role": "hospital",
            "phone": "+1-555-0300",
            "address": "456 Care Blvd",
            "city": "Los Angeles",
            "status": "active",
            "created_at": "2024-01-03",
        },
        {
            "id": 4,
            "name": "Metro Emergency Hospital",
            "email": "metro@hospital.com",
            "password": "admin123",
            "role": "hospital",
            "phone": "+1-555-0400",
            "address": "789 Emergency St",
            "city": "Chicago",
            "status": "active",
            "created_at": "2024-01-04",
        },
        {
            "id": 5,
            "name": "Central Blood Bank",
            "email": "central@bloodbank.com",
            "password": "admin123",
            "role": "bloodbank",
            "phone": "+1-555-0500",
            "city": "New York",
            "status": "active",
            "created_at": "2024-01-05",
        },
    ],
    "donors": [
        {
            "id": 1,
            "name": "John Smith",
            "email": "john@email.com",
            "password": "admin123",
            "phone": "+1-555-1001",
            "blood_group": "O+",
            "age": 28,
            "gender": "Male",
            "address": "101 Oak St",
            "city": "New York",
            "last_donation_date": "2024-01-15",
            "status": "active",
            "created_at": "2024-01-10",
        },
        {
            "id": 2,
            "name": "Sarah Johnson",
            "email": "sarah@email.com",
            "password": "admin123",
            "phone": "+1-555-1002",
            "blood_group": "A+",
            "age": 32,
            "gender": "Female",
            "address": "202 Pine Ave",
            "city": "Los Angeles",
            "last_donation_date": "2024-02-20",
            "status": "active",
            "created_at": "2024-01-11",
        },
    ],
    "inventory": [
        {
            "id": 1,
            "blood_group": "A+",
            "units": 45,
            "min_threshold": 10,
            "updated_at": "2024-04-01",
        },
        {
            "id": 2,
            "blood_group": "O+",
            "units": 52,
            "min_threshold": 10,
            "updated_at": "2024-04-01",
        },
    ],
    "blood_drives": [
        {
            "id": 1,
            "title": "Spring Blood Drive 2024",
            "location": "City Community Center",
            "city": "New York",
            "date": "2024-04-15",
            "status": "upcoming",
            "created_at": "2024-03-01",
        }
    ],
    "blood_requests": [
        {
            "id": 1,
            "hospital_id": 2,
            "blood_group": "O-",
            "quantity": 3,
            "priority": "critical",
            "patient_name": "Patient #1042",
            "reason": "Emergency surgery - trauma victim",
            "required_by_date": "2024-04-10",
            "status": "pending",
            "created_at": "2024-04-01",
        }
    ],
    "donation_history": [
        {
            "id": 1,
            "donor_id": 1,
            "drive_id": 1,
            "donation_date": "2024-01-15",
            "units": 1,
            "status": "completed",
            "notes": "Regular donation - no issues",
            "created_at": "2024-01-15",
        }
    ],
}


def _ensure_data_file():
    if not os.path.exists(DATA_FILE):
        with _lock:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(_default_data, f, indent=2)


def load_data():
    _ensure_data_file()
    with _lock:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)


def save_data(data):
    with _lock:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)


def _match(item, filters):
    if not filters:
        return True
    for k, v in filters.items():
        if k not in item:
            return False
        if item[k] != v:
            return False
    return True


def count(table, filters=None):
    data = load_data()
    return sum(1 for item in data.get(table, []) if _match(item, filters))


def sum_field(table, field, filters=None):
    data = load_data()
    total = 0
    for item in data.get(table, []):
        if _match(item, filters):
            total += item.get(field, 0) or 0
    return total


def select(table, filters=None, order_by=None, desc=False, limit=None):
    data = load_data()
    items = [item for item in data.get(table, []) if _match(item, filters)]
    if order_by:
        items.sort(key=lambda x: x.get(order_by) or "", reverse=desc)
    if limit:
        items = items[:limit]
    return items


def select_with_join_requests(
    filters=None, order_by="created_at", desc=True, limit=None
):
    data = load_data()
    requests = [r for r in data.get("blood_requests", []) if _match(r, filters)]
    # join users for hospital_name
    users = {u["id"]: u for u in data.get("users", [])}
    for r in requests:
        hosp = users.get(r.get("hospital_id"))
        r["hospital_name"] = hosp["name"] if hosp else None
    if order_by:
        requests.sort(key=lambda x: x.get(order_by) or "", reverse=desc)
    if limit:
        requests = requests[:limit]
    return requests


def get_by(table, **filters):
    data = load_data()
    for item in data.get(table, []):
        if _match(item, filters):
            return item
    return None


def insert(table, record):
    data = load_data()
    items = data.get(table, [])
    max_id = max([it.get("id", 0) for it in items], default=0)
    record = dict(record)
    record["id"] = max_id + 1
    if "created_at" not in record:
        record["created_at"] = datetime.utcnow().isoformat()
    items.append(record)
    data[table] = items
    save_data(data)
    return record


def update_by_id(table, id, updates):
    data = load_data()
    items = data.get(table, [])
    updated = False
    for i, item in enumerate(items):
        if item.get("id") == id:
            items[i] = {**item, **updates}
            updated = True
            break
    data[table] = items
    save_data(data)
    return updated


def update_where(table, filters, updates):
    data = load_data()
    items = data.get(table, [])
    count_upd = 0
    for i, item in enumerate(items):
        if _match(item, filters):
            items[i] = {**item, **updates}
            count_upd += 1
    data[table] = items
    save_data(data)
    return count_upd


# Convenience wrappers used by app


def init_passwords():
    data = load_data()
    hashed = "admin123"  # in file we store clear for demo; init endpoint will set hashes if desired
    emails = [
        "admin@bloodbridge.com",
        "citygen@hospital.com",
        "stmary@hospital.com",
        "metro@hospital.com",
        "central@bloodbank.com",
    ]
    for e in emails:
        for u in data.get("users", []):
            if u.get("email") == e:
                u["password"] = hashed
    donor_emails = [
        "john@email.com",
        "sarah@email.com",
        "michael@email.com",
        "emily@email.com",
        "robert@email.com",
        "lisa@email.com",
        "david@email.com",
        "jennifer@email.com",
    ]
    for e in donor_emails:
        for d in data.get("donors", []):
            if d.get("email") == e:
                d["password"] = hashed
    save_data(data)
    return True
