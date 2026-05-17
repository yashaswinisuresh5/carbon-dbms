# ============================================================
# Carbon Footprint System - Flask Backend
# DBMS Mini Project
# ============================================================
# Requirements: pip install flask bcrypt
# ============================================================

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import sqlite3
import bcrypt
import json
from datetime import datetime, date
import os

app = Flask(__name__)
app.secret_key = 'carbon_footprint_secret_key_2024'

# ============================================================
# DATABASE SETUP (AUTO-INITIALIZATION)
# ============================================================
def init_db():
    conn = sqlite3.connect('carbon_footprint.db')
    c = conn.cursor()
    
    # Create Users Table
    c.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        monthly_goal REAL DEFAULT 500.0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Try to add monthly_goal column if it doesn't exist (for backward compatibility)
    try:
        c.execute("ALTER TABLE Users ADD COLUMN monthly_goal REAL DEFAULT 500.0")
    except sqlite3.OperationalError:
        pass  # Column already exists

    
    # Create Activities Table
    c.execute('''
    CREATE TABLE IF NOT EXISTS Activities (
        activity_id INTEGER PRIMARY KEY AUTOINCREMENT,
        activity_name TEXT NOT NULL,
        category TEXT NOT NULL,
        unit TEXT NOT NULL,
        emission_factor REAL NOT NULL,
        description TEXT
    )''')
    
    # Create User_Activity Table
    c.execute('''
    CREATE TABLE IF NOT EXISTS User_Activity (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        activity_id INTEGER NOT NULL,
        quantity REAL NOT NULL,
        carbon_output REAL NOT NULL,
        date DATE NOT NULL,
        notes TEXT,
        FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
        FOREIGN KEY (activity_id) REFERENCES Activities(activity_id) ON DELETE CASCADE
    )''')

    # Insert default activities if empty
    c.execute("SELECT COUNT(*) FROM Activities")
    if c.fetchone()[0] == 0:
        default_activities = [
            ('Petrol Car Driving', 'Transport', 'km', 0.1920, 'Average petrol car'),
            ('Diesel Car Driving', 'Transport', 'km', 0.1710, 'Average diesel car'),
            ('Electric Car Driving', 'Transport', 'km', 0.0530, 'Average electric vehicle'),
            ('Motorcycle', 'Transport', 'km', 0.1030, 'Average motorcycle'),
            ('Bus Journey', 'Transport', 'km', 0.1050, 'Average local bus'),
            ('Flight (Domestic)', 'Transport', 'km', 0.2550, 'Short haul flight'),
            ('Grid Electricity', 'Electricity', 'kWh', 0.8500, 'Average grid electricity'),
            ('Solar Electricity', 'Electricity', 'kWh', 0.0410, 'Rooftop solar lifecycle emissions'),
            ('General Waste to Landfill', 'Waste', 'kg', 0.4500, 'Mixed municipal waste'),
            
            # ADVANCED: Carbon Offsets (Negative Emissions)
            ('Planted a Tree', 'Offset', 'tree', -22.0000, 'Tree absorbs CO2 over a year'),
            ('Composting', 'Offset', 'kg', -0.1500, 'Prevents methane from landfill'),
            ('Cycled Instead of Driving', 'Offset', 'km', -0.1920, 'Avoided petrol car emissions'),
            ('Renewable Energy Donated', 'Offset', 'kWh', -0.8500, 'Funded green energy')
        ]
        c.executemany('''INSERT INTO Activities (activity_name, category, unit, emission_factor, description)
                         VALUES (?, ?, ?, ?, ?)''', default_activities)
    
    conn.commit()
    conn.close()

# Initialize the database file and tables automatically
init_db()

# ============================================================
# DATABASE CONNECTION HELPER
# ============================================================
def get_db_connection():
    conn = sqlite3.connect('carbon_footprint.db')
    conn.row_factory = sqlite3.Row
    return conn

def execute_query(query, params=None, fetch=False):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        if fetch:
            result = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return result
        else:
            conn.commit()
            last_id = cursor.lastrowid
            conn.close()
            return last_id
    except sqlite3.Error as e:
        print(f"Query error: {e}")
        conn.rollback()
        conn.close()
        return None

# ============================================================
# ROUTES
# ============================================================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    return render_template('dashboard.html')



# ── AUTHENTICATION ──────────────────────────────────────────

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    name     = data.get('name', '').strip()
    email    = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not name or not email or not password:
        return jsonify({'success': False, 'message': 'All fields are required'}), 400

    existing = execute_query("SELECT user_id FROM Users WHERE email = ?", (email,), fetch=True)
    if existing:
        return jsonify({'success': False, 'message': 'Email already registered'}), 409

    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    user_id = execute_query(
        "INSERT INTO Users (name, email, password) VALUES (?, ?, ?)",
        (name, email, hashed_pw)
    )
    if user_id:
        session['user_id'] = user_id
        session['user_name'] = name
        return jsonify({'success': True, 'message': 'Registration successful', 'name': name})
    return jsonify({'success': False, 'message': 'Registration failed'}), 500


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email    = data.get('email', '').strip().lower()
    password = data.get('password', '')

    user = execute_query("SELECT user_id, name, email, password FROM Users WHERE email = ?", (email,), fetch=True)

    if user and bcrypt.checkpw(password.encode('utf-8'), user[0]['password'].encode('utf-8')):
        session['user_id'] = user[0]['user_id']
        session['user_name'] = user[0]['name']
        return jsonify({'success': True, 'name': user[0]['name']})

    return jsonify({'success': False, 'message': 'Invalid email or password'}), 401


@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})


@app.route('/api/set-goal', methods=['POST'])
def set_goal():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    data = request.get_json()
    new_goal = data.get('goal')
    
    if not new_goal:
        return jsonify({'success': False, 'message': 'Goal is required'}), 400
        
    execute_query("UPDATE Users SET monthly_goal = ? WHERE user_id = ?", (new_goal, session['user_id']))
    return jsonify({'success': True, 'message': 'Monthly goal updated successfully'})


@app.route('/api/export-csv')
def export_csv():
    if 'user_id' not in session:
        return redirect(url_for('index'))
        
    uid = session['user_id']
    records = execute_query(
        """SELECT ua.date, a.category, a.activity_name, ua.quantity, a.unit, ua.carbon_output, ua.notes
           FROM User_Activity ua
           JOIN Activities a ON ua.activity_id = a.activity_id
           WHERE ua.user_id = ?
           ORDER BY ua.date DESC""",
        (uid,), fetch=True
    )
    
    csv_data = "Date,Category,Activity,Quantity,Unit,Carbon Output (kg CO2),Notes\n"
    if records:
        for r in records:
            notes = str(r['notes']).replace(',', ' ') if r['notes'] else ''
            csv_data += f"{r['date']},{r['category']},{r['activity_name']},{r['quantity']},{r['unit']},{r['carbon_output']},{notes}\n"
            
    from flask import Response
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=carbon_report.csv"}
    )

# ── ACTIVITIES ───────────────────────────────────────────────

@app.route('/api/activities')
def get_activities():
    activities = execute_query(
        """SELECT activity_id, activity_name, category, unit, emission_factor, description
           FROM Activities
           ORDER BY category, activity_name""",
        fetch=True
    )
    if activities is None:
        return jsonify({'success': False, 'message': 'Could not fetch activities'}), 500

    grouped = {}
    for act in activities:
        cat = act['category']
        if cat not in grouped:
            grouped[cat] = []
        grouped[cat].append({
            'id':              act['activity_id'],
            'name':            act['activity_name'],
            'unit':            act['unit'],
            'emission_factor': float(act['emission_factor']),
            'description':     act['description']
        })

    return jsonify({'success': True, 'activities': grouped})


@app.route('/api/log-activity', methods=['POST'])
def log_activity():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401

    data        = request.get_json()
    activity_id = data.get('activity_id')
    quantity    = data.get('quantity')
    notes       = data.get('notes', '')

    if not activity_id or not quantity:
        return jsonify({'success': False, 'message': 'Missing fields'}), 400

    activity = execute_query(
        "SELECT activity_id, activity_name, emission_factor, unit FROM Activities WHERE activity_id = ?",
        (activity_id,), fetch=True
    )
    if not activity:
        return jsonify({'success': False, 'message': 'Invalid activity'}), 404

    emission_factor = float(activity[0]['emission_factor'])
    carbon_output   = round(float(quantity) * emission_factor, 4)
    today           = date.today().isoformat()

    record_id = execute_query(
        """INSERT INTO User_Activity (user_id, activity_id, quantity, carbon_output, date, notes)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (session['user_id'], activity_id, quantity, carbon_output, today, notes)
    )

    if record_id:
        return jsonify({
            'success':        True,
            'carbon_output':  carbon_output,
            'activity_name':  activity[0]['activity_name'],
            'unit':           activity[0]['unit'],
            'quantity':       quantity,
            'suggestions':    get_eco_suggestions(activity[0]['activity_name'], carbon_output)
        })
    return jsonify({'success': False, 'message': 'Failed to log activity'}), 500


# ── DASHBOARD & HISTORY ──────────────────────────────────────

@app.route('/api/dashboard')
def get_dashboard():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401

    uid = session['user_id']

    # Fetch User Goal
    user_data = execute_query("SELECT monthly_goal, name FROM Users WHERE user_id = ?", (uid,), fetch=True)
    monthly_goal = user_data[0]['monthly_goal'] if user_data else 500.0

    # ADVANCED: Gross Emissions vs Offsets
    gross_emissions = execute_query(
        "SELECT COALESCE(SUM(carbon_output), 0) AS gross FROM User_Activity WHERE user_id = ? AND carbon_output > 0",
        (uid,), fetch=True
    )[0]['gross']
    
    total_offsets = execute_query(
        "SELECT COALESCE(SUM(carbon_output), 0) AS offsets FROM User_Activity WHERE user_id = ? AND carbon_output < 0",
        (uid,), fetch=True
    )[0]['offsets']
    
    net_carbon = gross_emissions + total_offsets # total_offsets is negative

    total_activities = execute_query(
        "SELECT COUNT(id) AS count FROM User_Activity WHERE user_id = ?",
        (uid,), fetch=True
    )[0]['count']
    
    # Calculate current month's emissions for goal tracking
    current_month_total = execute_query(
        """SELECT COALESCE(SUM(ua.carbon_output), 0) AS current_month_carbon
           FROM User_Activity ua
           WHERE ua.user_id = ? AND strftime('%Y-%m', ua.date) = strftime('%Y-%m', 'now')""",
        (uid,), fetch=True
    )
    month_carbon = current_month_total[0]['current_month_carbon'] if current_month_total else 0

    categories = execute_query(
        """SELECT a.category,
                  SUM(ua.carbon_output) AS category_total,
                  COUNT(ua.id) AS activity_count
           FROM User_Activity ua
           JOIN Activities a ON ua.activity_id = a.activity_id
           WHERE ua.user_id = ? AND ua.carbon_output > 0
           GROUP BY a.category
           ORDER BY category_total DESC""",
        (uid,), fetch=True
    )

    weekly = execute_query(
        """SELECT ua.date, SUM(ua.carbon_output) AS daily_total
           FROM User_Activity ua
           WHERE ua.user_id = ? AND ua.date >= date('now', '-7 days')
           GROUP BY ua.date
           ORDER BY ua.date ASC""",
        (uid,), fetch=True
    )

    recent = execute_query(
        """SELECT ua.id, a.activity_name, a.category, a.unit,
                  ua.quantity, ua.carbon_output, ua.date, ua.notes
           FROM User_Activity ua
           JOIN Activities a ON ua.activity_id = a.activity_id
           WHERE ua.user_id = ?
           ORDER BY ua.date DESC, ua.id DESC
           LIMIT 5""",
        (uid,), fetch=True
    )

    def serialize(row):
        r = dict(row)
        for k, v in r.items():
            if hasattr(v, '__float__'):
                r[k] = float(v)
        return r

    return jsonify({
        'success':    True,
        'name':       session.get('user_name'),
        'goal':       monthly_goal,
        'month_carbon': month_carbon,
        'global_avg': 400.0, 
        'gross_emissions': gross_emissions,
        'total_offsets': abs(total_offsets),
        'net_carbon': net_carbon,
        'total_activities': total_activities,
        'categories': [serialize(c) for c in (categories or [])],
        'weekly':     [serialize(w) for w in (weekly or [])],
        'recent':     [serialize(r) for r in (recent or [])]
    })


@app.route('/api/leaderboard')
def get_leaderboard():
    if 'user_id' not in session:
        return jsonify({'success': False}), 401
        
    # Get top 5 users with the lowest net carbon footprint
    leaders = execute_query(
        """SELECT u.name, COALESCE(SUM(ua.carbon_output), 0) AS net_score
           FROM Users u
           LEFT JOIN User_Activity ua ON u.user_id = ua.user_id
           GROUP BY u.user_id, u.name
           ORDER BY net_score ASC
           LIMIT 10""", fetch=True
    )
    
    # Check if we have enough users to make it look active, if not add simulated anonymous data
    if leaders and len(leaders) < 3:
        simulated = [
            {'name': 'EcoJane', 'net_score': 150.4},
            {'name': 'GreenWarrior99', 'net_score': 210.5},
            {'name': 'PlanetSaver', 'net_score': 305.2}
        ]
        leaders.extend(simulated)
        leaders = sorted(leaders, key=lambda x: x['net_score'])[:10]
        
    return jsonify({'success': True, 'leaders': [dict(l) for l in leaders]})


@app.route('/api/history')
def get_history():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401

    uid      = session['user_id']
    page     = int(request.args.get('page', 1))
    per_page = 10
    offset   = (page - 1) * per_page

    records = execute_query(
        """SELECT ua.id, a.activity_name, a.category, a.unit, a.emission_factor,
                  ua.quantity, ua.carbon_output, ua.date, ua.notes
           FROM User_Activity ua
           JOIN Activities a ON ua.activity_id = a.activity_id
           WHERE ua.user_id = ?
           ORDER BY ua.date DESC, ua.id DESC
           LIMIT ? OFFSET ?""",
        (uid, per_page, offset), fetch=True
    )

    count = execute_query(
        "SELECT COUNT(*) AS total FROM User_Activity WHERE user_id = ?",
        (uid,), fetch=True
    )

    total_count = count[0]['total'] if count else 0

    return jsonify({
        'success': True,
        'records': [dict(r) for r in (records or [])],
        'total':   total_count,
        'pages':   (total_count + per_page - 1) // per_page,
        'page':    page
    })


@app.route('/api/delete-activity/<int:record_id>', methods=['DELETE'])
def delete_activity(record_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401

    result = execute_query(
        "DELETE FROM User_Activity WHERE id = ? AND user_id = ?",
        (record_id, session['user_id'])
    )
    return jsonify({'success': result is not None})


@app.route('/api/report')
def get_report():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401

    uid = session['user_id']

    top_activities = execute_query(
        """SELECT a.activity_name, a.category,
                  SUM(ua.carbon_output) AS total_emission,
                  COUNT(ua.id) AS times_logged
           FROM User_Activity ua
           JOIN Activities a ON ua.activity_id = a.activity_id
           WHERE ua.user_id = ?
           GROUP BY a.activity_id, a.activity_name, a.category
           ORDER BY total_emission DESC
           LIMIT 5""",
        (uid,), fetch=True
    )

    monthly = execute_query(
        """SELECT strftime('%Y-%m', ua.date) AS month,
                  SUM(ua.carbon_output) AS monthly_total
           FROM User_Activity ua
           WHERE ua.user_id = ?
           GROUP BY month
           ORDER BY month DESC
           LIMIT 6""",
        (uid,), fetch=True
    )

    return jsonify({
        'success':        True,
        'top_activities': [dict(t) for t in (top_activities or [])],
        'monthly':        [dict(m) for m in (monthly or [])]
    })


@app.route('/api/check-auth')
def check_auth():
    if 'user_id' in session:
        return jsonify({'authenticated': True, 'name': session.get('user_name')})
    return jsonify({'authenticated': False})


# ── ECO SUGGESTIONS ─────────────────────────────────────────

def get_eco_suggestions(activity_name, carbon_output):
    activity_lower = activity_name.lower()
    suggestions = []

    if 'car' in activity_lower and 'petrol' in activity_lower:
        suggestions = ["🚌 Switch to public transport — saves ~70% emissions", "🚗 Consider carpooling with colleagues", "⚡ Look into electric vehicles", "🚲 For short trips under 5km, cycle!"]
    elif 'flight' in activity_lower:
        suggestions = ["🚂 Train travel emits 6x less CO₂ than flying", "💻 Consider virtual meetings", "🌿 Choose direct routes"]
    elif 'electricity' in activity_lower:
        suggestions = ["☀️ Install solar panels", "💡 Switch to LED bulbs", "🔌 Unplug devices on standby"]
    elif 'beef' in activity_lower or 'lamb' in activity_lower:
        suggestions = ["🥗 Replace 1 beef meal/week with vegetables", "🐓 Chicken produces 4x less emissions", "🌱 Try plant-based proteins"]
    elif 'waste' in activity_lower:
        suggestions = ["♻️ Segregate waste", "🌱 Compost organic waste", "🛍️ Use reusable bags"]
    else:
        suggestions = ["🌱 Track your emissions regularly", "♻️ Reduce, Reuse, Recycle", "🌳 Plant a tree"]

    if carbon_output > 50:
        suggestions.insert(0, "⚠️ High impact activity! Prioritize reducing this emission source.")
    elif carbon_output > 10:
        suggestions.insert(0, "📊 Moderate impact. Small changes here can make a big difference.")
    else:
        suggestions.insert(0, "✅ Relatively low impact — keep it up!")

    return suggestions[:4]


if __name__ == '__main__':
    print("=" * 60)
    print("  Carbon Footprint System - DBMS Mini Project")
    print("  Starting Flask server on http://localhost:5000")
    print("=" * 60)
    app.run(debug=True, port=5000, host="0.0.0.0")
