from flask import Flask, render_template_string, request, redirect, session, url_for
import math
import uuid
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey123"

# ================= EMAIL CONFIG =================
SENDER_EMAIL = "yourgmail@gmail.com"       # Replace with your Gmail
SENDER_PASSWORD = "your_app_password"      # Replace with Gmail App Password
ADMIN_EMAIL = "manojgowdaa17@gmail.com"

# ================= ADMIN LOGIN =================
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# ================= STORAGE =================
volunteers_data = []

# Admin-managed tasks/events
tasks_data = [
    {
        "id": str(uuid.uuid4()),
        "title": "Lalbagh Tree Plantation Drive",
        "category": "ongoing",
        "date": "2026-05-10",
        "area": "Lalbagh",
        "description": "Community-led environmental restoration through tree plantation.",
        "skills": ["environment", "logistics"]
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Whitefield Blood Donation Camp",
        "category": "future",
        "date": "2026-06-15",
        "area": "Whitefield",
        "description": "Upcoming blood donation and health awareness initiative.",
        "skills": ["medical", "management"]
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Koramangala Food Distribution",
        "category": "previous",
        "date": "2026-03-11",
        "area": "Koramangala",
        "description": "Successfully distributed food kits to underserved communities.",
        "skills": ["food_distribution", "driving"]
    }
]

# Bengaluru Areas Coordinates
AREA_COORDS = {
    "Whitefield": (12.9698, 77.7500),
    "Koramangala": (12.9352, 77.6245),
    "Electronic City": (12.8456, 77.6603),
    "Marathahalli": (12.9591, 77.6974),
    "Indiranagar": (12.9784, 77.6408),
    "HSR Layout": (12.9116, 77.6474),
    "Jayanagar": (12.9250, 77.5938),
    "BTM Layout": (12.9166, 77.6101),
    "Lalbagh": (12.9507, 77.5848)
}

# ================= EMAIL FUNCTION =================
def send_email(to_email, subject, body):
    try:
        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
        server.quit()
    except Exception as e:
        print("Email sending failed:", e)

# ================= HELPERS =================
def area_to_coords(area):
    return AREA_COORDS.get(area, (12.9716, 77.5946))

# ================= HOME =================
@app.route("/")
def home():
    previous = [t for t in tasks_data if t["category"] == "previous"]
    ongoing = [t for t in tasks_data if t["category"] == "ongoing"]
    future = [t for t in tasks_data if t["category"] == "future"]

    def render_cards(events):
        cards = ""
        for e in events:
            cards += f'''
            <div class="glass-card p-3 mb-3">
                <h5>{e['title']}</h5>
                <p><b>Area:</b> {e['area']}</p>
                <p><b>Date:</b> {e['date']}</p>
                <p>{e['description']}</p>
            </div>
            '''
        return cards or "<p>No events available</p>"

    map_markers = ""
    for t in tasks_data:
        lat, lon = area_to_coords(t["area"])
        color = "red" if t["category"] == "previous" else "green" if t["category"] == "ongoing" else "blue"
        map_markers += f"L.circleMarker([{lat}, {lon}], {{color:'{color}', radius:8}}).addTo(map).bindPopup('{t['title']} - {t['category'].title()}');\n"

    return render_template_string(f'''
<!DOCTYPE html>
<html>
<head>
<title>Smart Volunteer Allocation</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
body {{
    background: linear-gradient(rgba(0,0,0,0.65), rgba(0,0,0,0.75)), url('https://images.unsplash.com/photo-1522202176988-66273c2fd55f') center/cover fixed;
    color:white;
    font-family: Arial;
}}
.hero {{padding:120px 20px; text-align:center;}}
.glass-card {{background: rgba(255,255,255,0.15); backdrop-filter: blur(10px); border-radius:20px; color:white;}}
.section-bg {{padding:60px 20px; border-radius:20px; margin-bottom:30px; animation: fadebg 12s infinite;}}
@keyframes fadebg {{
0% {{background: rgba(255,0,0,0.15);}}
33% {{background: rgba(0,255,0,0.15);}}
66% {{background: rgba(0,0,255,0.15);}}
100% {{background: rgba(255,0,0,0.15);}}
}}
#map {{height:500px; border-radius:20px;}}
.legend span {{display:inline-block; width:15px; height:15px; margin-right:8px; border-radius:50%;}}
.article {{background: rgba(255,255,255,0.12); padding:20px; border-radius:15px;}}
</style>
</head>
<body>

<nav class="navbar navbar-dark bg-dark px-4">
    <h3>Volunteer AI Bengaluru</h3>
    <div>
        <a href="/register" class="btn btn-success">Register</a>
        <a href="/dashboard" class="btn btn-info">Dashboard</a>
    </div>
</nav>

<section class="hero">
    <h1 class="display-3">Smart Volunteer Allocation Platform</h1>
    <p class="lead">Connecting Bengaluru volunteers with meaningful social impact missions through intelligent task coordination.</p>
    <p>Our platform manages disaster relief, blood donation drives, environmental campaigns, food distribution, and social outreach programs.</p>
</section>

<div class="container">

<div class="section-bg">
<h2>Event Sessions Across Bengaluru</h2>
<div class="legend mb-3">
<p><span style="background:red"></span>Previous &nbsp; <span style="background:green"></span>Ongoing &nbsp; <span style="background:blue"></span>Future</p>
</div>
<div id="map"></div>
</div>

<div class="row">
<div class="col-md-4"><div class="section-bg"><h3>Previous Sessions</h3>{render_cards(previous)}</div></div>
<div class="col-md-4"><div class="section-bg"><h3>Ongoing Sessions</h3>{render_cards(ongoing)}</div></div>
<div class="col-md-4"><div class="section-bg"><h3>Future Sessions</h3>{render_cards(future)}</div></div>
</div>

<div class="mt-5">
<h2>Volunteer Articles & Impact Stories</h2>
<div class="article mt-3">
<h4>How Food Drives Are Transforming Bengaluru Communities</h4>
<p>Volunteer-led food programs in Koramangala and BTM Layout continue to support hundreds of families monthly.</p>
</div>
<div class="article mt-3">
<h4>Environmental Sustainability Through Tree Plantation</h4>
<p>Our Lalbagh and Jayanagar campaigns contribute to cleaner, greener neighborhoods.</p>
</div>
<div class="article mt-3">
<h4>Medical Volunteers Strengthening Public Health</h4>
<p>Blood donation and emergency medical camps are expanding across Whitefield and Electronic City.</p>
</div>
</div>

<footer class="text-center mt-5 mb-4">
<p>For feedback or queries: manojgowdaa17@gmail.com</p>
</footer>

</div>

<script>
var map = L.map('map').setView([12.9716,77.5946], 11);
L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png').addTo(map);
{map_markers}
</script>

</body>
</html>
''')

# ================= REGISTER =================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        area = request.form["area"]
        lat, lon = area_to_coords(area)

        volunteer = {
            "id": str(uuid.uuid4()),
            "name": request.form["name"],
            "email": request.form["email"],
            "skills": request.form.getlist("skills"),
            "availability": request.form.getlist("availability"),
            "city": "Bengaluru",
            "area": area,
            "lat": lat,
            "lon": lon
        }

        volunteers_data.append(volunteer)

        send_email(volunteer["email"], "Volunteer Registration Successful",
                   f"Hello {volunteer['name']}, thank you for registering in Bengaluru Volunteer AI System.")

        send_email(ADMIN_EMAIL, "New Volunteer Registered",
                   f"Name: {volunteer['name']}\nEmail: {volunteer['email']}\nArea: {volunteer['area']}")

        return redirect("/")

    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
<title>Register</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<style>
body {background: linear-gradient(rgba(0,0,0,.6), rgba(0,0,0,.6)), url('https://images.unsplash.com/photo-1517048676732-d65bc937f952') center/cover fixed; color:white;}
.card {background: rgba(255,255,255,0.12); backdrop-filter: blur(12px); border-radius:20px;}
</style>
</head>
<body>
<div class="container mt-5">
<div class="card p-4 shadow-lg">
<h2>Volunteer Registration - Bengaluru</h2>
<form method="POST">
<input class="form-control my-2" name="name" placeholder="Full Name" required>
<input class="form-control my-2" type="email" name="email" placeholder="Email" required>

<h5>Skills</h5>
<div>
<input type="checkbox" name="skills" value="medical"> Medical
<input type="checkbox" name="skills" value="logistics"> Logistics
<input type="checkbox" name="skills" value="rescue"> Rescue
<input type="checkbox" name="skills" value="teaching"> Teaching
<input type="checkbox" name="skills" value="food_distribution"> Food Distribution
<input type="checkbox" name="skills" value="technical_support"> Technical Support
<input type="checkbox" name="skills" value="environment"> Environment
<input type="checkbox" name="skills" value="management"> Management
</div>

<h5 class="mt-3">Availability</h5>
<div>
<input type="checkbox" name="availability" value="morning"> Morning
<input type="checkbox" name="availability" value="afternoon"> Afternoon
<input type="checkbox" name="availability" value="evening"> Evening
<input type="checkbox" name="availability" value="night"> Night
</div>

<h5 class="mt-3">City</h5>
<input class="form-control" value="Bengaluru" readonly>

<h5 class="mt-3">Area</h5>
<input class="form-control" list="areaList" name="area" placeholder="Type Bengaluru area..." required>
<datalist id="areaList">
<option value="Whitefield">
<option value="Koramangala">
<option value="Electronic City">
<option value="Marathahalli">
<option value="Indiranagar">
<option value="HSR Layout">
<option value="Jayanagar">
<option value="BTM Layout">
<option value="Lalbagh">
</datalist>

<button class="btn btn-success mt-4">Submit</button>
</form>
</div>
</div>
</body>
</html>
''')

# ================= SECRET ADMIN LOGIN =================
@app.route("/control_center", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if request.form["username"] == ADMIN_USERNAME and request.form["password"] == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect("/admin_panel")
        return "<h3>Invalid credentials</h3>"

    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
<title>Control Center</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<style>
body {background: linear-gradient(rgba(0,0,0,.7), rgba(0,0,0,.7)), url('https://images.unsplash.com/photo-1497366754035-f200968a6e72') center/cover fixed;}
.card {background: rgba(255,255,255,0.12); color:white; backdrop-filter: blur(12px); border-radius:20px;}
</style>
</head>
<body>
<div class="container mt-5">
<div class="card p-4 shadow-lg">
<h2>Admin Control Center</h2>
<form method="POST">
<input class="form-control my-2" name="username" placeholder="Username" required>
<input class="form-control my-2" type="password" name="password" placeholder="Password" required>
<button class="btn btn-danger mt-3">Login</button>
</form>
</div>
</div>
</body>
</html>
''')

# ================= ADMIN PANEL =================
@app.route("/admin_panel", methods=["GET", "POST"])
def admin_panel():
    if not session.get("admin"):
        return redirect("/control_center")

    if request.method == "POST":
        tasks_data.append({
            "id": str(uuid.uuid4()),
            "title": request.form["title"],
            "category": request.form["category"],
            "date": request.form["date"],
            "area": request.form["area"],
            "description": request.form["description"],
            "skills": request.form.getlist("skills")
        })
        return redirect("/admin_panel")

    volunteer_rows = "".join([
        f"<tr><td>{v['name']}</td><td>{v['email']}</td><td>{', '.join(v['skills'])}</td><td>{v['area']}</td></tr>"
        for v in volunteers_data
    ])

    task_rows = "".join([
        f"<tr><td>{t['title']}</td><td>{t['category']}</td><td>{t['date']}</td><td>{t['area']}</td></tr>"
        for t in tasks_data
    ])

    return render_template_string(f'''
<!DOCTYPE html>
<html>
<head>
<title>Admin Panel</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<style>
body {{background: linear-gradient(rgba(0,0,0,.7), rgba(0,0,0,.7)), url('https://images.unsplash.com/photo-1521737604893-d14cc237f11d') center/cover fixed; color:white;}}
.glass {{background: rgba(255,255,255,0.12); backdrop-filter: blur(12px); border-radius:20px;}}
</style>
</head>
<body>
<div class="container mt-5">
<h1>Admin Management Dashboard</h1>
<a href="/admin_logout" class="btn btn-warning mb-4">Logout</a>

<div class="glass p-4 mb-5">
<h3>Create New Volunteer Session</h3>
<form method="POST">
<input class="form-control my-2" name="title" placeholder="Task Title" required>
<select class="form-control my-2" name="category">
<option value="previous">Previous</option>
<option value="ongoing">Ongoing</option>
<option value="future">Future</option>
</select>
<input class="form-control my-2" type="date" name="date" required>
<input class="form-control my-2" list="areaList" name="area" placeholder="Area" required>
<datalist id="areaList">
<option value="Whitefield"><option value="Koramangala"><option value="Electronic City"><option value="Marathahalli"><option value="Indiranagar"><option value="HSR Layout"><option value="Jayanagar"><option value="BTM Layout"><option value="Lalbagh">
</datalist>
<textarea class="form-control my-2" name="description" placeholder="Description"></textarea>
<button class="btn btn-success mt-3">Create Session</button>
</form>
</div>

<div class="glass p-4 mb-5">
<h3>Registered Volunteers</h3>
<table class="table table-dark table-striped">
<tr><th>Name</th><th>Email</th><th>Skills</th><th>Area</th></tr>
{volunteer_rows}
</table>
</div>

<div class="glass p-4">
<h3>Managed Sessions</h3>
<table class="table table-dark table-striped">
<tr><th>Title</th><th>Category</th><th>Date</th><th>Area</th></tr>
{task_rows}
</table>
</div>

</div>
</body>
</html>
''')

# ================= ADMIN LOGOUT =================
@app.route("/admin_logout")
def admin_logout():
    session.pop("admin", None)
    return redirect("/")

# ================= DASHBOARD =================
@app.route("/dashboard")
def dashboard():
    return render_template_string(f'''
<!DOCTYPE html>
<html>
<head>
<title>Dashboard</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<style>
body {{background: linear-gradient(rgba(0,0,0,.7), rgba(0,0,0,.7)), url('https://images.unsplash.com/photo-1504384308090-c894fdcc538d') center/cover fixed; color:white;}}
.card {{background: rgba(255,255,255,.12); backdrop-filter: blur(10px); border-radius:20px;}}
</style>
</head>
<body>
<div class="container text-center mt-5">
<h1>System Dashboard</h1>
<div class="row mt-4">
<div class="col-md-6"><div class="card p-4"><h3>Total Volunteers</h3><h1>{len(volunteers_data)}</h1></div></div>
<div class="col-md-6"><div class="card p-4"><h3>Total Sessions</h3><h1>{len(tasks_data)}</h1></div></div>
</div>
<a href="/" class="btn btn-light mt-4">Home</a>
</div>
</body>
</html>
''')

# ================= RUN =================
if __name__ == "__main__":
    print("Starting Smart Volunteer Allocation System...")
    print("Open browser: http://127.0.0.1:5000")
    print("Secret admin login: http://127.0.0.1:5000/control_center")
    app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=False)