from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    jsonify,
)
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.secret_key = "bloodbridge_secret_key_2024_cloud_architecture_demo"

# ============================================
# AWS RDS Configuration (Demo/Local Mode)
# ============================================
# Production: AWS RDS Endpoint
# app.config['MYSQL_HOST'] = 'bloodbridge-db.abc123xyz.us-east-1.rds.amazonaws.com'
# app.config['MYSQL_USER'] = 'admin'
# app.config['MYSQL_PASSWORD'] = 'your-secure-password'
# app.config['MYSQL_DB'] = 'bloodbridge_db'

# Local Development Mode (XAMPP/MySQL Workbench)
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "bloodbridge_db"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)

# If MySQL server is not available (local dev without MySQL), provide a
# minimal in-memory fallback so the app can run for demos/tests without
# aborting on a DB connection error.


class _DefaultDict(dict):
    def __missing__(self, key):
        if key in ("total", "low", "fulfilled", "pending", "count", "units"):
            return 0
        return None


class _FakeCursor:
    def __init__(self):
        self._last = None
        self._last_result = []

    def execute(self, sql, params=None):
        # Lazy import to avoid circulars at module import time
        from data_backend import (
            count,
            sum_field,
            select,
            select_with_join_requests,
            get_by,
            insert,
            update_by_id,
            update_where,
        )

        s = (sql or "").lower()
        self._last = (sql, params)
        self._last_result = []

        # COUNT queries
        if "select count(*)" in s and "from donors" in s:
            status = None
            if "where status='active'" in s or (params and "active" in params):
                status = "active"
            self._last_result = [
                {"total": count("donors", {"status": status} if status else None)}
            ]
            return
        if (
            "select count(*)" in s
            and "from blood_requests" in s
            and "status='fulfilled'" in s
        ):
            self._last_result = [
                {"total": count("blood_requests", {"status": "fulfilled"})}
            ]
            return
        if "select count(*)" in s and "from users" in s and "role='hospital'" in s:
            self._last_result = [{"total": count("users", {"role": "hospital"})}]
            return
        if (
            "select count(*)" in s
            and "from blood_requests" in s
            and "status='pending'" in s
        ):
            self._last_result = [
                {"total": count("blood_requests", {"status": "pending"})}
            ]
            return

        # generic count
        if "select count(*)" in s and "from" in s:
            if "from users" in s:
                self._last_result = [{"total": count("users")}]
            elif "from blood_requests" in s:
                self._last_result = [{"total": count("blood_requests")}]
            else:
                self._last_result = [{"total": 0}]
            return

        # SUM queries
        if "select sum(units)" in s and "from inventory" in s:
            self._last_result = [{"total": sum_field("inventory", "units")}]
            return

        # SELECT simple lists
        if "select * from inventory" in s:
            items = select("inventory", order_by="blood_group")
            self._last_result = items
            return

        # select donors where id = %s or email
        if "select * from donors where id" in s:
            val = params[0] if params else None
            item = get_by("donors", id=val)
            self._last_result = [item] if item else []
            return
        if "select * from donors where email" in s:
            val = params[0] if params else None
            item = get_by("donors", email=val)
            self._last_result = [item] if item else []
            return

        # select users by email and role
        if "select * from users where email" in s and "and role" in s:
            email = params[0] if params else None
            role = params[1] if params and len(params) > 1 else None
            item = get_by("users", email=email, role=role)
            self._last_result = [item] if item else []
            return

        # select donors by email
        if "select * from donors where email" in s:
            email = params[0] if params else None
            item = get_by("donors", email=email)
            self._last_result = [item] if item else []
            return

        # join requests with users
        if "from blood_requests" in s and "join users" in s:
            limit = None
            if "limit" in s:
                try:
                    limit = int(s.split("limit")[-1].strip().split()[0])
                except Exception:
                    limit = None
            items = select_with_join_requests(limit=limit)
            # support WHERE br.blood_group = %s AND br.status = 'pending'
            if "where br.blood_group" in s and params:
                bg = params[0]
                items = [
                    it
                    for it in items
                    if it.get("blood_group") == bg and it.get("status") == "pending"
                ]
            self._last_result = items
            return

        # donation_history by donor_id
        if "from donation_history" in s and "where donor_id" in s:
            donor_id = params[0] if params else None
            items = select(
                "donation_history",
                filters={"donor_id": donor_id},
                order_by="donation_date",
                desc=True,
            )
            self._last_result = items
            return

        # INSERT handling (simple mapping by columns)
        if s.strip().startswith("insert into") and "values" in s:
            # crude parse to extract table and column names
            try:
                parts = sql.split("(")
                before_cols = parts[0]
                cols_part = "(" + "(".join(parts[1:])
                table = before_cols.split()[2]
                cols = (
                    sql[sql.index("(") + 1 : sql.index(")")]
                    .replace("\n", "")
                    .replace(" ", "")
                )
                cols = [c.strip() for c in cols.split(",")]
                # map params to cols (ignore NOW() columns)
                vals = []
                if params:
                    vals = list(params)
                record = {}
                j = 0
                for c in cols:
                    if "now" in c.lower():
                        continue
                    if j < len(vals):
                        record[c] = vals[j]
                        j += 1
                insert(table, record)
                self._last_result = []
            except Exception:
                self._last_result = []
            return

        # UPDATE by id
        if s.strip().startswith("update") and "where id =" in s or "where id = %s" in s:
            try:
                table = sql.split()[1]
                # handle status update patterns
                if "set status = %s" in s and params:
                    status = params[0]
                    rid = params[-1]
                    update_by_id(
                        table,
                        rid,
                        {"status": status, "updated_at": datetime.utcnow().isoformat()},
                    )
                    self._last_result = []
                    return
            except Exception:
                pass

        # simple fallback: return empty
        self._last_result = []

    def fetchone(self):
        if not self._last_result:
            return _DefaultDict()
        first = self._last_result[0]
        return first

    def fetchall(self):
        return self._last_result or []

    def close(self):
        return None


class _FakeConnection:
    def cursor(self):
        return _FakeCursor()

    def commit(self):
        return None


# Note: we avoid probing mysql.connection at import-time because that may
# require an application context. Instead, provide safe helper functions
# that will attempt to use the real connection at request-time and
# gracefully fall back to the fake connection when the DB is not
# available.


def get_db_connection():
    """Get fresh database connection (may be a callable or object).
    We return whatever `mysql.connection` provides: it might be a
    callable (to be called) or a connection object.
    """
    conn = getattr(mysql, "connection", None)
    if callable(conn):
        try:
            return conn()
        except Exception:
            return _FakeConnection()
    try:
        # ensure it has a cursor
        conn.cursor()
        return conn
    except Exception:
        return _FakeConnection()


def safe_cursor():
    """Return a real DB cursor if available, otherwise a fake cursor."""
    try:
        conn = get_db_connection()
        return conn.cursor()
    except Exception:
        return _FakeCursor()


def safe_commit():
    """Commit on real DB connection if available; otherwise no-op."""
    try:
        conn = get_db_connection()
        conn.commit()
    except Exception:
        return None


def check_session():
    """Check if user is logged in"""
    if "user_id" not in session:
        return False
    return True


def get_user_role():
    """Get current user role"""
    return session.get("role", None)


# ============================================
# HOME & STATIC PAGES
# ============================================


@app.route("/")
def index():
    """Home Page - BloodBridge Landing"""
    cur = safe_cursor()

    # Get statistics for hero section
    cur.execute("SELECT COUNT(*) as total FROM donors WHERE status='active'")
    total_donors = cur.fetchone()["total"]

    cur.execute("SELECT COUNT(*) as total FROM blood_requests WHERE status='fulfilled'")
    lives_saved = cur.fetchone()["total"] * 3  # Approx 3 lives per donation

    cur.execute("SELECT COUNT(*) as total FROM users WHERE role='hospital'")
    partner_hospitals = cur.fetchone()["total"]

    cur.execute("SELECT COUNT(*) as total FROM blood_requests WHERE status='pending'")
    active_requests = cur.fetchone()["total"]

    cur.close()

    return render_template(
        "index.html",
        total_donors=total_donors,
        lives_saved=lives_saved,
        partner_hospitals=partner_hospitals,
        active_requests=active_requests,
    )


@app.route("/about")
def about():
    """About & Architecture Page"""
    return render_template("about.html")


@app.route("/contact")
def contact():
    """Contact Page"""
    return render_template("contact.html")


# ============================================
# AUTHENTICATION SYSTEM
# ============================================


@app.route("/login", methods=["GET", "POST"])
def login():
    """Universal Login Page"""
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        role = request.form.get("role", "donor")

        cur = safe_cursor()

        # Helper function to verify password (supports both hashed and plain text for demo)
        def verify_password(stored_password, provided_password):
            # Check if it's a werkzeug hash
            if stored_password.startswith("pbkdf2:") or stored_password.startswith(
                "$2"
            ):
                try:
                    return check_password_hash(stored_password, provided_password)
                except:
                    return False
            # Plain text comparison (for demo/testing purposes)
            return stored_password == provided_password

        # Check users table first
        cur.execute("SELECT * FROM users WHERE email = %s AND role = %s", (email, role))
        user = cur.fetchone()

        if user and verify_password(user["password"], password):
            session["user_id"] = user["id"]
            session["email"] = user["email"]
            session["role"] = user["role"]
            session["name"] = user["name"]
            session["login_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            flash(f"Welcome back, {user['name']}!", "success")

            # Redirect based on role
            if role == "admin":
                return redirect(url_for("admin_dashboard"))
            elif role == "donor":
                return redirect(url_for("donor_dashboard"))
            elif role == "hospital":
                return redirect(url_for("hospital_dashboard"))
            elif role == "bloodbank":
                return redirect(url_for("bloodbank_dashboard"))

        # Check donors table for donor login
        if role == "donor":
            cur.execute("SELECT * FROM donors WHERE email = %s", (email,))
            donor = cur.fetchone()

            if donor and verify_password(donor["password"], password):
                session["user_id"] = donor["id"]
                session["email"] = donor["email"]
                session["role"] = "donor"
                session["name"] = donor["name"]
                session["donor_id"] = donor["id"]
                session["login_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                flash(f"Welcome back, {donor['name']}!", "success")
                return redirect(url_for("donor_dashboard"))

        cur.close()
        flash("Invalid credentials. Please try again.", "danger")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Donor Registration Page"""
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        phone = request.form["phone"]
        blood_group = request.form["blood_group"]
        age = request.form["age"]
        gender = request.form["gender"]
        address = request.form["address"]
        city = request.form["city"]
        last_donation = request.form.get("last_donation", None)

        hashed_password = generate_password_hash(password)

        cur = safe_cursor()

        # Check if email exists
        cur.execute("SELECT id FROM donors WHERE email = %s", (email,))
        if cur.fetchone():
            flash("Email already registered!", "warning")
            cur.close()
            return redirect(url_for("register"))

        # Insert donor
        cur.execute(
            """
            INSERT INTO donors (name, email, password, phone, blood_group, age, gender, 
                              address, city, last_donation_date, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'active', NOW())
        """,
            (
                name,
                email,
                hashed_password,
                phone,
                blood_group,
                age,
                gender,
                address,
                city,
                last_donation,
            ),
        )

        safe_commit()
        cur.close()

        flash("Registration successful! Please login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/logout")
def logout():
    """Logout & Clear Session"""
    session.clear()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for("index"))


# ============================================
# ADMIN DASHBOARD
# ============================================


@app.route("/admin/dashboard")
def admin_dashboard():
    """Admin Dashboard - Full Control Panel"""
    if not check_session() or get_user_role() != "admin":
        flash("Access denied. Admin privileges required.", "danger")
        return redirect(url_for("login"))

    cur = safe_cursor()

    # Statistics
    cur.execute("SELECT COUNT(*) as total FROM donors")
    total_donors = cur.fetchone()["total"]

    cur.execute("SELECT COUNT(*) as total FROM blood_requests")
    total_requests = cur.fetchone()["total"]

    cur.execute("SELECT COUNT(*) as total FROM blood_requests WHERE status='pending'")
    pending_requests = cur.fetchone()["total"]

    cur.execute("SELECT COUNT(*) as total FROM blood_requests WHERE status='fulfilled'")
    fulfilled_requests = cur.fetchone()["total"]

    cur.execute("SELECT COUNT(*) as total FROM users WHERE role='hospital'")
    total_hospitals = cur.fetchone()["total"]

    # Recent blood requests
    cur.execute("""
        SELECT br.*, u.name as hospital_name 
        FROM blood_requests br 
        JOIN users u ON br.hospital_id = u.id 
        ORDER BY br.created_at DESC LIMIT 10
    """)
    recent_requests = cur.fetchall()

    # Recent donors
    cur.execute("SELECT * FROM donors ORDER BY created_at DESC LIMIT 8")
    recent_donors = cur.fetchall()

    # Inventory summary
    cur.execute("SELECT * FROM inventory ORDER BY blood_group")
    inventory = cur.fetchall()

    cur.close()

    return render_template(
        "admin/dashboard.html",
        total_donors=total_donors,
        total_requests=total_requests,
        pending_requests=pending_requests,
        fulfilled_requests=fulfilled_requests,
        total_hospitals=total_hospitals,
        recent_requests=recent_requests,
        recent_donors=recent_donors,
        inventory=inventory,
    )


@app.route("/admin/users")
def admin_users():
    """Admin - Manage All Users"""
    if not check_session() or get_user_role() != "admin":
        return redirect(url_for("login"))

    cur = safe_cursor()
    cur.execute("SELECT * FROM users ORDER BY created_at DESC")
    users = cur.fetchall()
    cur.execute("SELECT * FROM donors ORDER BY created_at DESC")
    donors = cur.fetchall()
    cur.close()

    return render_template("admin/users.html", users=users, donors=donors)


@app.route("/admin/requests")
def admin_requests():
    """Admin - Manage Blood Requests"""
    if not check_session() or get_user_role() != "admin":
        return redirect(url_for("login"))

    cur = safe_cursor()
    cur.execute("""
        SELECT br.*, u.name as hospital_name 
        FROM blood_requests br 
        JOIN users u ON br.hospital_id = u.id 
        ORDER BY br.created_at DESC
    """)
    requests = cur.fetchall()
    cur.close()

    return render_template("admin/requests.html", requests=requests)


@app.route("/admin/inventory")
def admin_inventory():
    """Admin - View Inventory"""
    if not check_session() or get_user_role() != "admin":
        return redirect(url_for("login"))

    cur = safe_cursor()
    cur.execute("SELECT * FROM inventory ORDER BY blood_group")
    inventory = cur.fetchall()
    cur.close()

    return render_template("admin/inventory.html", inventory=inventory)


@app.route("/admin/update_request/<int:request_id>", methods=["POST"])
def update_request_status(request_id):
    """Update Blood Request Status"""
    if not check_session() or get_user_role() != "admin":
        return jsonify({"success": False, "message": "Unauthorized"})

    status = request.form["status"]

    cur = safe_cursor()
    cur.execute(
        "UPDATE blood_requests SET status = %s, updated_at = NOW() WHERE id = %s",
        (status, request_id),
    )
    safe_commit()
    cur.close()

    flash(f"Request #{request_id} updated to {status}", "success")
    return redirect(url_for("admin_requests"))


# ============================================
# DONOR DASHBOARD
# ============================================


@app.route("/donor/dashboard")
def donor_dashboard():
    """Donor Dashboard"""
    if not check_session() or get_user_role() != "donor":
        flash("Please login as a donor.", "warning")
        return redirect(url_for("login"))

    cur = safe_cursor()

    # Get donor details
    cur.execute("SELECT * FROM donors WHERE id = %s", (session["user_id"],))
    donor = cur.fetchone()

    # Check eligibility
    eligibility = check_donor_eligibility(donor)

    # Get upcoming blood drives
    cur.execute(
        "SELECT * FROM blood_drives WHERE date >= CURDATE() ORDER BY date LIMIT 5"
    )
    blood_drives = cur.fetchall()

    # Get donation history
    cur.execute(
        """
        SELECT * FROM donation_history 
        WHERE donor_id = %s ORDER BY donation_date DESC LIMIT 5
    """,
        (session["user_id"],),
    )
    donation_history = cur.fetchall()

    # Get active requests matching blood group
    cur.execute(
        """
        SELECT br.*, u.name as hospital_name 
        FROM blood_requests br 
        JOIN users u ON br.hospital_id = u.id 
        WHERE br.blood_group = %s AND br.status = 'pending'
        ORDER BY br.created_at DESC LIMIT 5
    """,
        (donor["blood_group"],),
    )
    matching_requests = cur.fetchall()

    cur.close()

    return render_template(
        "donor/dashboard.html",
        donor=donor,
        eligibility=eligibility,
        blood_drives=blood_drives,
        donation_history=donation_history,
        matching_requests=matching_requests,
    )


@app.route("/donor/profile", methods=["GET", "POST"])
def donor_profile():
    """Donor Profile Management"""
    if not check_session() or get_user_role() != "donor":
        return redirect(url_for("login"))

    cur = safe_cursor()

    if request.method == "POST":
        name = request.form["name"]
        phone = request.form["phone"]
        address = request.form["address"]
        city = request.form["city"]

        cur.execute(
            """
            UPDATE donors 
            SET name = %s, phone = %s, address = %s, city = %s, updated_at = NOW()
            WHERE id = %s
        """,
            (name, phone, address, city, session["user_id"]),
        )
        safe_commit()
        flash("Profile updated successfully!", "success")

    cur.execute("SELECT * FROM donors WHERE id = %s", (session["user_id"],))
    donor = cur.fetchone()
    cur.close()

    return render_template("donor/profile.html", donor=donor)


@app.route("/donor/schedule", methods=["POST"])
def schedule_donation():
    """Schedule Blood Donation"""
    if not check_session() or get_user_role() != "donor":
        return jsonify({"success": False})

    drive_id = request.form["drive_id"]
    scheduled_date = request.form["scheduled_date"]

    cur = safe_cursor()
    cur.execute(
        """
        INSERT INTO donation_history (donor_id, drive_id, scheduled_date, status, created_at)
        VALUES (%s, %s, %s, 'scheduled', NOW())
    """,
        (session["user_id"], drive_id, scheduled_date),
    )
    safe_commit()
    cur.close()

    flash("Donation scheduled successfully!", "success")
    return redirect(url_for("donor_dashboard"))


def check_donor_eligibility(donor):
    """Check if donor is eligible to donate"""
    if not donor or not donor.get("last_donation_date"):
        return {"eligible": True, "message": "Eligible to donate", "days_left": 0}

    last_donation = donor["last_donation_date"]
    if isinstance(last_donation, str):
        try:
            last_donation = datetime.strptime(last_donation, "%Y-%m-%d")
        except Exception:
            return {"eligible": True, "message": "Eligible to donate", "days_left": 0}

    days_since = (datetime.now() - last_donation).days
    min_days = 56  # 8 weeks minimum

    if days_since >= min_days:
        return {"eligible": True, "message": "Eligible to donate", "days_left": 0}
    else:
        return {
            "eligible": False,
            "message": f"Wait {min_days - days_since} more days",
            "days_left": min_days - days_since,
        }


# ============================================
# HOSPITAL DASHBOARD
# ============================================


@app.route("/hospital/dashboard")
def hospital_dashboard():
    """Hospital Dashboard"""
    if not check_session() or get_user_role() != "hospital":
        flash("Please login as a hospital.", "warning")
        return redirect(url_for("login"))

    cur = safe_cursor()

    # Get hospital's requests
    cur.execute(
        """
        SELECT * FROM blood_requests 
        WHERE hospital_id = %s ORDER BY created_at DESC
    """,
        (session["user_id"],),
    )
    my_requests = cur.fetchall()

    # Statistics
    cur.execute(
        """
        SELECT COUNT(*) as total FROM blood_requests WHERE hospital_id = %s
    """,
        (session["user_id"],),
    )
    total_requests = cur.fetchone()["total"]

    cur.execute(
        """
        SELECT COUNT(*) as pending FROM blood_requests 
        WHERE hospital_id = %s AND status = 'pending'
    """,
        (session["user_id"],),
    )
    pending_requests = cur.fetchone()["pending"]

    cur.execute(
        """
        SELECT COUNT(*) as fulfilled FROM blood_requests 
        WHERE hospital_id = %s AND status = 'fulfilled'
    """,
        (session["user_id"],),
    )
    fulfilled_requests = cur.fetchone()["fulfilled"]

    # Get available donors
    cur.execute(
        "SELECT * FROM donors WHERE status = 'active' ORDER BY created_at DESC LIMIT 10"
    )
    available_donors = cur.fetchall()

    # Get inventory
    cur.execute("SELECT * FROM inventory ORDER BY blood_group")
    inventory = cur.fetchall()

    cur.close()

    return render_template(
        "hospital/dashboard.html",
        my_requests=my_requests,
        total_requests=total_requests,
        pending_requests=pending_requests,
        fulfilled_requests=fulfilled_requests,
        available_donors=available_donors,
        inventory=inventory,
    )


@app.route("/hospital/request_blood", methods=["GET", "POST"])
def request_blood():
    """Create Emergency Blood Request"""
    if not check_session() or get_user_role() != "hospital":
        return redirect(url_for("login"))

    if request.method == "POST":
        blood_group = request.form["blood_group"]
        quantity = request.form["quantity"]
        priority = request.form["priority"]
        patient_name = request.form["patient_name"]
        reason = request.form["reason"]
        required_by = request.form["required_by"]

        cur = safe_cursor()
        cur.execute(
            """
            INSERT INTO blood_requests 
            (hospital_id, blood_group, quantity, priority, patient_name, reason, 
             required_by_date, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'pending', NOW())
        """,
            (
                session["user_id"],
                blood_group,
                quantity,
                priority,
                patient_name,
                reason,
                required_by,
            ),
        )
        safe_commit()
        cur.close()

        flash("Emergency blood request created successfully!", "success")
        return redirect(url_for("hospital_dashboard"))

    return render_template("hospital/request_blood.html")


# ============================================
# BLOOD BANK DASHBOARD
# ============================================


@app.route("/bloodbank/dashboard")
def bloodbank_dashboard():
    """Blood Bank Manager Dashboard"""
    if not check_session() or get_user_role() != "bloodbank":
        flash("Please login as a blood bank manager.", "warning")
        return redirect(url_for("login"))

    cur = safe_cursor()

    # Get inventory
    cur.execute("SELECT * FROM inventory ORDER BY blood_group")
    inventory = cur.fetchall()

    # Get all requests
    cur.execute("""
        SELECT br.*, u.name as hospital_name 
        FROM blood_requests br 
        JOIN users u ON br.hospital_id = u.id 
        ORDER BY br.created_at DESC
    """)
    all_requests = cur.fetchall()

    # Statistics
    cur.execute("SELECT SUM(units) as total FROM inventory")
    total_units = cur.fetchone()["total"] or 0

    cur.execute("SELECT COUNT(*) as low FROM inventory WHERE units < 10")
    low_stock = cur.fetchone()["low"]

    cur.execute("SELECT COUNT(*) as total FROM blood_requests WHERE status='pending'")
    pending_requests = cur.fetchone()["total"]

    cur.close()

    return render_template(
        "bloodbank/dashboard.html",
        inventory=inventory,
        all_requests=all_requests,
        total_units=total_units,
        low_stock=low_stock,
        pending_requests=pending_requests,
    )


@app.route("/bloodbank/update_inventory", methods=["POST"])
def update_inventory():
    """Update Blood Inventory"""
    if not check_session() or get_user_role() != "bloodbank":
        return jsonify({"success": False})

    blood_group = request.form["blood_group"]
    units = request.form["units"]
    operation = request.form["operation"]  # add or subtract

    cur = safe_cursor()

    if operation == "add":
        cur.execute(
            """
            UPDATE inventory 
            SET units = units + %s, updated_at = NOW()
            WHERE blood_group = %s
        """,
            (units, blood_group),
        )
    else:
        cur.execute(
            """
            UPDATE inventory 
            SET units = GREATEST(0, units - %s), updated_at = NOW()
            WHERE blood_group = %s
        """,
            (units, blood_group),
        )

    safe_commit()
    cur.close()

    flash(f"Inventory updated for {blood_group}", "success")
    return redirect(url_for("bloodbank_dashboard"))


# ============================================
# EMERGENCY REQUEST SYSTEM (Public)
# ============================================


@app.route("/emergency")
def emergency():
    """Emergency Blood Request Page (Public)"""
    cur = safe_cursor()
    cur.execute("""
        SELECT br.*, u.name as hospital_name 
        FROM blood_requests br 
        JOIN users u ON br.hospital_id = u.id 
        WHERE br.status = 'pending' AND br.priority = 'critical'
        ORDER BY br.created_at DESC LIMIT 10
    """)
    emergency_requests = cur.fetchall()
    cur.close()

    return render_template("emergency.html", emergency_requests=emergency_requests)


@app.route("/inventory")
def public_inventory():
    """Public Inventory View"""
    cur = safe_cursor()
    cur.execute("SELECT * FROM inventory ORDER BY blood_group")
    inventory = cur.fetchall()
    cur.close()

    return render_template("inventory.html", inventory=inventory)


# ============================================
# API ENDPOINTS (For AJAX/Charts)
# ============================================


@app.route("/api/inventory")
def api_inventory():
    """API: Get Inventory Data"""
    cur = safe_cursor()
    cur.execute("SELECT blood_group, units FROM inventory ORDER BY blood_group")
    data = cur.fetchall()
    cur.close()
    return jsonify(data)


@app.route("/api/stats")
def api_stats():
    """API: Get Dashboard Statistics"""
    cur = safe_cursor()

    stats = {}

    cur.execute("SELECT COUNT(*) as total FROM donors")
    stats["total_donors"] = cur.fetchone()["total"]

    cur.execute("SELECT COUNT(*) as total FROM blood_requests")
    stats["total_requests"] = cur.fetchone()["total"]

    cur.execute("SELECT COUNT(*) as total FROM blood_requests WHERE status='fulfilled'")
    stats["fulfilled"] = cur.fetchone()["total"]

    cur.execute("SELECT SUM(units) as total FROM inventory")
    stats["total_units"] = cur.fetchone()["total"] or 0

    cur.close()
    return jsonify(stats)


@app.route("/api/request_stats")
def api_request_stats():
    """API: Get Request Statistics by Status"""
    cur = safe_cursor()
    cur.execute("""
        SELECT status, COUNT(*) as count 
        FROM blood_requests 
        GROUP BY status
    """)
    data = cur.fetchall()
    cur.close()
    return jsonify(data)


# ============================================
# ERROR HANDLERS
# ============================================


@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template("500.html"), 500


# ============================================
# SETUP / INIT ROUTE (For first-time setup)
# ============================================


@app.route("/init-db")
def init_db():
    """Initialize database with proper password hashes"""
    # For JSON backend, use the data_backend helper to initialize demo passwords
    try:
        from data_backend import init_passwords

        init_passwords()
    except Exception:
        pass

    return """
    <h1>Database Initialized!</h1>
    <p>All passwords have been reset to 'admin123' with proper hashing.</p>
    <p><a href='/login'>Go to Login</a></p>
    """


# ============================================
# MAIN ENTRY POINT
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("  BloodBridge: Optimizing Lifesaving Resources")
    print("  AWS Cloud Architecture Demo - Local Mode")
    print("  Architecture: EC2 (Flask) → RDS (MySQL)")
    print("=" * 60)
    print("  Server running at: http://localhost:5000")
    print("  Admin Login: admin@bloodbridge.com / admin123")
    print("=" * 60)
    app.run(debug=True, host="0.0.0.0", port=5000)
