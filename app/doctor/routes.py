from flask import render_template, request, flash, redirect, url_for

from app.db import get_db
from . import doctor_bp


# TODO: Implement
@doctor_bp.route("/")
def overview():
    return render_template("doctor/overview.html")


# TODO: Usecase Step 1: Selecting a patient
@doctor_bp.route('/search', methods=['GET', 'POST'])
def search_patient():
    if request.method == "POST":
        query = request.form.get("query")
        db = get_db()

        patients = db.find_patients(query)
        print(f"Found patients with length {len(patients)}")

        if len(patients) > 1:
            # must be multiple entries that it found
            # render template for this, with patients enabled
            # Asks user to select the concrete patient
            return render_template("doctor/usecase/step1_search_patient.html", patients=patients)
        elif len(patients) == 1:
            # get patient details
            # FIXME: lookup the format of the patient dict
            patient_id = db.get_patient_details(patients[0]["SVNr"])
            return redirect(url_for("doctor.select_appointment", patient_id=patient_id))
        else:
            flash("No patients found", "danger")
    # GET Action: initially just render the template
    return render_template("doctor/usecase/step1_search_patient.html")


# TODO: Usecase Step 2: Selecting an appointment

@doctor_bp.route('/patient/<int:patient_id>/appointments', methods=['GET'])
def select_appointment(patient_id: int):
    db = get_db()
    patient = db.get_patient_details(patient_id)
    # render the html template with the patient details
    # which contain not only the patient name etc., but also all of their appointments!
    return render_template("doctor/usecase/step2_select_appointment.html", patient=patient)


# TODO: Usecase Step 3: Adding a treatment
@doctor_bp.route('/patient/<int:patient_id>/appointment/<int:appt_id>/add-treatment', methods=['GET', 'POST'])
def add_treatment(patient_id, appt_id):
    db = get_db()

    if request.method == "POST":
        db = get_db()
        description = request.form.get("description")
        cost = request.form.get("cost")
        med_string = request.form.get("medication_names_list")
        # decode the encoded query details
        # and save it in the database.
        print("Entered details: ")
        print(description)
        print(cost)
        medList = parseMedString(med_string, db)
        print(medList)

        success = db.add_treatment(patient_id, appt_id, description, float(cost), medList)
        # if the saving was successful (should be), display a success message, and redirect to the page.
        if success:
            return render_template("doctor/usecase/step3_success.html", patient_id=patient_id, appt_id=appt_id)
    # else initially pass the med_list alongside the appt ID
    return render_template("doctor/usecase/step3_add_treatment.html", patient_id=patient_id, appt_id=appt_id,
                           all_meds=db.get_all_med_names())


def parseMedString(med_string: str, db) -> list:
    med_names_list = []

    # TODO: Validate against the med list

    raw_meds = med_string.split(";")
    for med_name in raw_meds:
        if med_name.strip():
            med_names_list.append(med_name.strip())

    return med_names_list
