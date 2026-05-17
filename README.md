# 🌿 EcoTrack - Net-Zero Carbon Footprint Tracker

EcoTrack is an advanced, full-stack **DBMS Mini Project** designed to track, analyze, and offset carbon footprints. It goes beyond simple calculators by introducing a **Net-Zero Architecture**, allowing users to log both *Emissions* (positive footprint) and *Offsets* (negative footprint).

## 🏆 Contest-Winning Features
- **Net-Zero Tracking Logic:** Calculates Gross Emissions minus Total Offsets to yield a Net Carbon Footprint.
- **Monthly Budget Goals:** Set limits (e.g., 500kg CO₂) and track progress via dynamic progress bars.
- **Gamification & Badges:** Unlock "Eco Warrior" and "Eco Master" badges by keeping your emissions below global averages.
- **Global Leaderboard:** Ranks users based on their Net Score (Emissions - Offsets).
- **Data Export (CSV):** One-click download of your entire footprint history for Excel analysis.
- **Premium Glassmorphism UI:** Built with Bootstrap 5, featuring frosted glass panels and smooth CSS animations.
- **Dynamic Charts:** Powered by `Chart.js` to visualize Real-time Activity Impact and Category Breakdowns.

## ⚙️ Tech Stack
- **Frontend:** HTML5, CSS3 (Glassmorphism), JavaScript, Bootstrap 5, Chart.js
- **Backend:** Python (Flask)
- **Database:** SQLite (Auto-initializes on startup with predefined Emission Factors)

## 🚀 How to Run Locally

### 1. Requirements
Ensure you have Python installed on your system.

### 2. Installation
Clone the repository and install the required Python libraries:
```bash
pip install flask bcrypt
```

### 3. Launch the Application
Run the backend server:
```bash
python app.py
```
*Note: The database (`carbon_footprint.db`) is generated and populated automatically the first time you run this script!*

### 4. View the App
Open your web browser and go to:
👉 `http://127.0.0.1:5000`

---
*Created as an advanced DBMS Mini Project emphasizing proper relational database structures, complex aggregate queries, and real-world application logic.*
