from flask import Flask, render_template, redirect, request, url_for, session

app = Flask(__name__)

# ------------------ ADMIN USERS (TEMP DATA) ------------------
users = [
    {"id": 1, "name": "John Doe", "email": "john@example.com", "role": "Patient", "status": "Pending"},
    {"id": 2, "name": "Dr. Smith", "email": "smith@hospital.com", "role": "Doctor", "status": "Active"}
]
# ------------------ AMBULANCE REQUESTS ------------------
ambulance_requests = []


app.secret_key = "supersecretkey123"  # for session

# ------------------ GLOBAL DATA ------------------
sos_requests = []  # SOS requests

# ------------------ BASIC PAGES ------------------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/service")
def service():
    return render_template("service.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

# ------------------ LOGIN ------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form.get("name")
        role = request.form.get("role")
        latitude = request.form.get("latitude")
        longitude = request.form.get("longitude")

        session["name"] = name
        session["role"] = role
        session["lat"] = latitude
        session["lng"] = longitude

        if role == "patient":
            return redirect(url_for("patient_dashboard"))
        elif role == "doctor":
            return redirect(url_for("doctor_dashboard"))
        elif role == "healthworker":
            return redirect(url_for("healthworker_dashboard"))
        elif role == "admin":
            return redirect(url_for("admin_dashboard"))
        else:
            return "Invalid Role Selected"

    return render_template("login.html")

# ------------------ DASHBOARDS ------------------
@app.route("/patient")
def patient_dashboard():
    latitude = session.get("lat")
    longitude = session.get("lng")
    name = session.get("name", "Patient")
    return render_template("patient.html", latitude=latitude, longitude=longitude, name=name)

# @app.route("/doctor")
# def doctor_dashboard():
#     tele_rooms = session.get("tele_rooms", [])
#     return render_template("doctor.html", sos_requests=sos_requests, tele_rooms=tele_rooms)

@app.route("/doctor")
def doctor_dashboard():
    tele_rooms = session.get("tele_rooms", [])
    return render_template(
        "doctor.html",
        sos_requests=sos_requests,
        tele_rooms=tele_rooms,
        ambulance_requests=ambulance_requests
    )


@app.route("/healthworker")
def healthworker_dashboard():
    return render_template("healthworker.html")

# @app.route("/admin")
# def admin_dashboard():
#     return render_template("admin.html")
@app.route("/admin")
def admin_dashboard():
    return render_template(
        "admin.html",
        users=users,
        ambulance_requests=ambulance_requests
    )
# @app.route("/accept_ambulance/<int:index>", methods=["POST"])
# def accept_ambulance(index):
#     ambulance_requests[index]["status"] = "Accepted"
#     return redirect(request.referrer)

@app.route("/accept_ambulance/<int:index>", methods=["POST"])
def accept_ambulance(index):
    ambulance_requests[index]["status"] = "Accepted"
    return redirect("/ambulance_driver")


@app.route("/ambulance_driver")
def ambulance_driver():
    return render_template(
        "ambulance_driver.html",
        ambulance_requests=ambulance_requests
    )


# ------------------ SOS FLOW ------------------
@app.route("/send_sos", methods=["POST"])
def send_sos():
    name = session.get("name", "Unknown")
    lat = session.get("lat")
    lng = session.get("lng")

    sos_requests.append({
        "name": name,
        "lat": lat,
        "lng": lng,
        "status": "Pending"
    })
    return "OK"

@app.route("/accept_sos/<int:index>", methods=["POST"])
def accept_sos(index):
    if 0 <= index < len(sos_requests):
        sos_requests[index]["status"] = "Accepted"
    return redirect(url_for("doctor_dashboard"))

# ------------------ TELEMEDICINE ------------------
@app.route("/telemedicine_room", methods=["POST"])
def telemedicine_room():
    room = request.form.get("room")
    patient = request.form.get("patient")

    if "tele_rooms" not in session:
        session["tele_rooms"] = []
    
    tele_rooms = session["tele_rooms"]
    tele_rooms.append({"room": room, "patient": patient})
    session["tele_rooms"] = tele_rooms

    return "OK"



# ------------------ ADMIN ACTIONS ------------------

@app.route("/admin/accept/<int:user_id>", methods=["POST"])
def accept_user(user_id):
    for u in users:
        if u["id"] == user_id:
            u["status"] = "Active"
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/reject/<int:user_id>", methods=["POST"])
def reject_user(user_id):
    for u in users:
        if u["id"] == user_id:
            u["status"] = "Rejected"
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/delete/<int:user_id>", methods=["POST"])
def delete_user(user_id):
    global users
    users = [u for u in users if u["id"] != user_id]
    return redirect(url_for("admin_dashboard"))


# @app.route("/admin/add", methods=["POST"])
# def add_user():
#     new_id = users[-1]["id"] + 1 if users else 1
#     users.append({
#         "id": new_id,
#         "name": f"User {new_id}",
#         "email": f"user{new_id}@mail.com",
#         "role": "Patient",
#         "status": "Pending"
#     })
#     return redirect(url_for("admin_dashboard"))

@app.route("/admin/add_user", methods=["POST"])
def add_user():
    new_id = users[-1]["id"] + 1 if users else 1

    users.append({
        "id": new_id,
        "name": request.form["name"],
        "email": request.form["email"],
        "phone": request.form["phone"],
        "role": request.form["role"],
        "status": "Pending"
    })

    return redirect(url_for("admin_dashboard"))

@app.route("/admin/add_user_form")
def add_user_form():
    return render_template("add_user.html")

# @app.route("/call_ambulance", methods=["POST"])
# def call_ambulance():
#     name = session.get("name", "Unknown")
#     lat = session.get("lat")
#     lng = session.get("lng")

#     ambulance_requests.append({
#         "name": name,
#         "lat": lat,
#         "lng": lng,
#         "status": "Requested"
#     })

#     return "OK"

@app.route("/call_ambulance", methods=["POST"])
def call_ambulance():
    ambulance_requests.append({
        "name": session.get("name"),
        "lat": session.get("lat"),
        "lng": session.get("lng"),
        "status": "Requested"
    })
    return "OK"

@app.route("/driver_track/<int:index>")
def driver_track(index):
    amb = ambulance_requests[index]

    lat = amb["lat"]
    lng = amb["lng"]

    google_map_url = f"https://www.google.com/maps/dir/?api=1&destination={lat},{lng}&travelmode=driving"

    return redirect(google_map_url)

# ------------------ RUN ------------------
if __name__ == "__main__":
    app.run()
