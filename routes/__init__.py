"""
routes/__init__.py
All Flask routes for the TBM dashboard
"""

from flask import render_template, request, redirect, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from utils import load_user_data, load_patient_data, get_patient_data_by_id
import pandas as pd
import os, uuid

USER_CSV            = "users.csv"                      # username | password | role | patient_id
TBM_DATA_CSV        = os.path.join("data", "tbm_data.csv")


# --------------------------------------------------------------------------- #
#  ROUTES
# --------------------------------------------------------------------------- #
def init_routes(app):
    # ─────────────────────────── HOME ─────────────────────────── #
    @app.route("/home")
    def home():
        return render_template("home.html")

    @app.route("/")  # root → /home
    def index():
        return redirect(url_for("home"))

    # ────────────────────────── LOGIN ────────────────────────── #
    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            users     = load_user_data()
            username  = request.form["username"]
            password  = request.form["password"]

            row = users[users["username"] == username]
            if row.empty or not check_password_hash(row.iloc[0]["password"], password):
                return render_template("login.html", error="Invalid credentials")

            # Save minimal session
            session["username"]   = username
            session["role"]       = row.iloc[0]["role"]
            session["patient_id"] = row.iloc[0]["patient_id"]

            # Redirect logic
            if session["role"] == "Admin":
                return redirect(url_for("dashboard"))
            else:
                return redirect(url_for("data_entry"))

        return render_template("login.html")

    # ───────────────────────── SIGN-UP ───────────────────────── #
    @app.route("/signup", methods=["GET", "POST"])
    def signup():
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]
            role     = request.form["role"]

            users = load_user_data()
            if username in users["username"].values:
                return render_template("signup.html", error="Username already exists.")

            # Generate patient_id for clients
            patient_id = (
                request.form.get("patient_id") or str(uuid.uuid4())
                if role == "Client" else ""
            )

            # Store user
            hashed_pw = generate_password_hash(password)
            new_user  = pd.DataFrame(
                [{"username": username, "password": hashed_pw,
                  "role": role, "patient_id": patient_id}]
            )
            users = pd.concat([users, new_user], ignore_index=True)
            users.to_csv(USER_CSV, index=False)

            # Start session and redirect
            session.update(username=username, role=role, patient_id=patient_id)
            return redirect(url_for("login"))


        return render_template("signup.html")

   
    # ───────────── DATA-ENTRY (CSF) ───────────── #
    @app.route("/data_entry", methods=["GET", "POST"])
    def data_entry():
        if "username" not in session or session["role"] != "Client":
            return redirect(url_for("login"))

        if request.method == "POST":
            cols = [
                "Sr No.", "Date", "Sample Code", "Patient_ID",
                "TLC", "L%", "P%", "Sugar", "Protein"
            ]
            df = (
                pd.read_csv(TBM_DATA_CSV)
                if os.path.exists(TBM_DATA_CSV) else pd.DataFrame(columns=cols)
            )
            next_sr = len(df) + 1
            new_row = {
                "Sr No.":   next_sr,
                "Date":     request.form["date"],
                "Sample Code": request.form["sample_code"],
                "Patient_ID":  session["patient_id"],
                "TLC":      request.form["tlc"],
                "L%":       request.form["l_percent"],
                "P%":       request.form["p_percent"],
                "Sugar":    request.form["sugar"],
                "Protein":  request.form["protein"],
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv(TBM_DATA_CSV, index=False)
            return redirect(url_for("dashboard"))

        return render_template("data_entry.html")

    # ───────────────────── DASHBOARD ───────────────────── #
    @app.route("/dashboard")
    def dashboard():
        if "username" not in session:
            return redirect(url_for("login"))

        role   = session["role"]
        lab_df = load_patient_data()

        if role == "Admin":
            return render_template(
                "admin_dashboard.html",
                data=lab_df.to_dict(orient="records")
            )

        # Client dashboard
        pid      = session["patient_id"]
        lab_rows = get_patient_data_by_id(lab_df, pid).to_dict(orient="records")

        return render_template("client_dashboard.html", data=lab_rows)


    # ───────────────────── LOGOUT ───────────────────── #
    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("home"))
