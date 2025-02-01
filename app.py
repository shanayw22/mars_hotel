from flask import Flask, render_template, request, redirect, url_for
import re
from datetime import datetime
import pandas as pd

app = Flask(__name__)


form_data = {}


def is_valid_email(email):
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email))


def is_valid_phone(phone):
    return bool(re.match(r"^\+?[1-9]\d{1,14}$", phone))


def is_valid_date(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def save_to_csv(data):
    df = pd.DataFrame([data])
    df.to_csv('collected_data/mars_application_submissions.csv', mode='a', header=False, index=False)


@app.route("/stage1", methods=["GET", "POST"])
def stage1():
    global form_data
    if request.method == "POST":
        full_name = request.form["full_name"]
        dob = request.form["dob"]
        nationality = request.form["nationality"]
        email = request.form["email"]
        phone = request.form["phone"]

        
        if not full_name or not dob or not nationality or not email or not phone:
            return "Please fill in all fields.", 400
        elif not is_valid_email(email):
            return "Please enter a valid email.", 400
        elif not is_valid_phone(phone):
            return "Please enter a valid phone number.", 400
        
        # Store data and proceed to next stage
        form_data = {
            "full_name": full_name,
            "dob": dob,
            "nationality": nationality,
            "email": email,
            "phone": phone
        }
        return redirect(url_for("stage2"))
    
    return render_template("index.html", stage=1)


@app.route("/stage2", methods=["GET", "POST"])
def stage2():
    global form_data
    if request.method == "POST":
        departure_date = request.form["departure_date"]
        return_date = request.form["return_date"]
        accommodation = request.form["accommodation"]
        special_requests = request.form["special_requests"]

        
        if not departure_date or not return_date:
            return "Please select departure and return dates.", 400
        elif not is_valid_date(departure_date) or not is_valid_date(return_date):
            return "Please enter valid dates.", 400
        
        
        form_data.update({
            "departure_date": departure_date,
            "return_date": return_date,
            "accommodation": accommodation,
            "special_requests": special_requests
        })
        return redirect(url_for("stage3"))
    
    return render_template("index.html", stage=2)


@app.route("/stage3", methods=["GET", "POST"])
def stage3():
    global form_data
    if request.method == "POST":
        health_declaration = request.form.get("health_declaration")
        emergency_contact = request.form["emergency_contact"]
        medical_conditions = request.form["medical_conditions"]

        # Validate the fields
        if not emergency_contact:
            return "Please provide emergency contact information.", 400

        # Store data and proceed to submission
        form_data.update({
            "health_declaration": health_declaration,
            "emergency_contact": emergency_contact,
            "medical_conditions": medical_conditions
        })
        
        # Save the form data to a CSV file
        save_to_csv(form_data)

        return redirect(url_for("confirmation"))
    
    return render_template("index.html", stage=3)

# Route for Confirmation
@app.route("/confirmation")
def confirmation():
    return render_template("confirmation.html", form_data=form_data)

# Main route to go to the first stage
@app.route("/")
def index():
    return redirect(url_for("stage1"))

if __name__ == "__main__":
    app.run(debug=True)