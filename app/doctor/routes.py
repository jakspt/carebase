from flask import render_template, request

from app.db import get_db
from . import doctor_bp


# TODO: Implement
@doctor_bp.route('/')
def overview():
    return render_template('doctor/overview.html')


# TODO: Usecase Step 1: Selecting a patient
@doctor_bp.route('/search', methods=['GET', 'POST'])
def search_patient():
    if request.method == "POST":
        query = request.form.get("query")
        db = get_db()

        patients = db.find_patients(query)

        if len(patients) > 1:
            # must be multiple entries that it found
            # render template for this, with patients enabled
            pass
        if len(patients) == 1:
            pass
            # must be the one
        else:
            # show error message on re-render
            pass
    # on GET, just render the template


# TODO: Usecase Step 2: Selecting an appointment

@doctor_bp.route('/patient/<int:patient_id>/appointments', methods=['GET'])
def select_appointment(patient_id: int):
    db = get_db()
    patient_details = db.get_patient_details(patient_id)
    # render the html template with the patient details
    # which contain not only the patient name etc., but also all of their appointments!


# TODO: Usecase Step 3: Adding a treatment
@doctor_bp.route('/patient/<int:patient_id>/appointment/<int:appt_id>/add-treatment', methods=['POST'])
def add_treatment(patient_id, appt_id):
    if request.method == "POST":
        db = get_db()
        # decode the encoded query details
        # and save it in the database.
        # if the saving was successful, display a success message.
    pass
