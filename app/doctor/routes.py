import json
from datetime import date
from multiprocessing import Value

from flask import flash, redirect, render_template, request, url_for

from app.db import get_db

from . import doctor_bp


@doctor_bp.route("/")
def overview():
    return render_template("doctor/overview.html")


# Step 1: Selecting a patient
@doctor_bp.route("/search", methods=["GET", "POST"])
def search_patient():
    if request.method == "POST":
        query = request.form.get("query")
        if not query:
            raise ValueError("Query was not provided.")
        db = get_db()

        patients = db.find_patients(query)
        print(f"Found patients with length {len(patients)}")

        if len(patients) > 1:
            # must be multiple entries that it found
            # render template for this, with patients enabled
            # Asks user to select the concrete patient
            return render_template(
                "doctor/usecase/step1_search_patient.html", patients=patients
            )
        elif len(patients) == 1:
            # get patient details
            # FIXME: lookup the format of the patient dict
            patient_id = db.get_patient_details(patients[0]["SVNr"])
            return redirect(url_for("doctor.select_appointment", patient_id=patient_id))
        else:
            flash("Keine Patienten gefunden", "danger")
    # GET Action: initially just render the template
    return render_template("doctor/usecase/step1_search_patient.html")


# Step 2: Selecting an appointment
@doctor_bp.route("/patient/<int:patient_id>/appointments", methods=["GET"])
def select_appointment(patient_id: int):
    db = get_db()
    patient = db.get_patient_details(patient_id)
    return render_template(
        "doctor/usecase/step2_select_appointment.html", patient=patient
    )


# Step 3: Adding a treatment (+ meds)
@doctor_bp.route(
    "/patient/<int:patient_id>/appointment/<int:appt_id>/add-treatment",
    methods=["GET", "POST"],
)
def add_treatment(patient_id, appt_id):
    db = get_db()

    if request.method == "POST":
        db = get_db()
        description = request.form.get("description")
        cost = request.form.get("cost")
        med_string = request.form.get("medications_list", "")
        med_list = []

        if description is None or cost is None:
            raise ValueError(
                "Error adding treatment Some of the required fields are missing"
            )
        if med_string.strip():
            med_list = json.loads(med_string)

        print("Entered details: ")
        print(description)
        print(cost)
        print(med_list)

        success = db.add_treatment(
            patient_id, appt_id, description, float(cost), med_list
        )
        # if the saving was successful (should be), display a success message, and redirect to the page.
        if success:
            return render_template(
                "doctor/usecase/step3_success.html",
                patient_id=patient_id,
                appt_id=appt_id,
            )
        else:
            flash("Behandlung konnte nicht hinzugefügt werden", "danger")
    # else initially pass the med_list alongside the appt ID
    return render_template(
        "doctor/usecase/step3_add_treatment.html",
        patient_id=patient_id,
        appt_id=appt_id,
        all_meds=db.get_all_meds(),
    )


@doctor_bp.route("/report")
def report():
    # default to jan 1st of this year if date is not provided
    start_date = request.args.get("start_date")
    if not start_date:
        start_date = f"{date.today().year}-01-01"

    db = get_db()
    raw_data = db.get_doctor_report(start_date)

    chart_labels, chart_values = aggregate_chart_data(raw_data)

    print(start_date)
    return render_template(
        "doctor/report/report.html",
        start_date=start_date,
        chart_labels=chart_labels,
        chart_values=chart_values,
        raw_data=raw_data,
    )


def aggregate_chart_data(raw_data):
    aggregate = {}

    for row in raw_data:
        doctor_id = row["id"]

        # initialize if this doctor has not been processed before
        if doctor_id not in aggregate:
            aggregate[doctor_id] = {
                "id": doctor_id,  # necessary to allow for sorting
                "name": row["name"],
                "total": 0.0,
            }
        aggregate[doctor_id]["total"] += row["total_costs"]

    aggregate_list = list(aggregate.values())
    sorted_list = sorted(aggregate_list, key=lambda x: x["total"], reverse=True)

    labels = [f"{item['name']} (#{item['id']})" for item in sorted_list]
    values = [item["total"] for item in sorted_list]

    return labels, values
