from flask import jsonify, render_template, request

from app.db import *

from . import clerk_bp


@clerk_bp.route('/')
def overview():
    return render_template('clerk/overview.html')


@clerk_bp.route('/appointment')
def appointment():
    return render_template('clerk/appointment.html')


@clerk_bp.route('/report')
def report():
    return render_template('clerk/report.html')
    

@clerk_bp.route('/api/clerks/search')
def search_clerks():
    query = request.args.get('q', '').lower()
    
    db = get_db()
    clerks = db.get_all_clerks()
    
    # Filter based on query
    filtered = [
        c for c in clerks
        if query in c['name'].lower() or query in str(c['svnr'])
    ]
    
    return jsonify({"clerks": filtered})

@clerk_bp.route('/api/patients/search')
def search_patients():

    query = request.args.get('q', '').lower()
    
    db = get_db()

    patients = db.get_all_patients()
    
    # Filter based on query
    filtered = [
        p for p in patients
        if query in p['name'].lower() or query in p['svnr']
    ]
    
    return jsonify({"patients": filtered})

@clerk_bp.route('/api/doctors')
def get_doctors():
    
    db = get_db()

    doctors = db.get_all_doctors()
    
    return jsonify({"doctors": doctors})

@clerk_bp.route('/api/timeslots')
def get_timeslots():
    date = request.args.get('date', '')
    doctor_svnr = request.args.get('doctor_svnr', '')
    patient_svnr = request.args.get('patient_svnr', '')
    
    if not date or not doctor_svnr:
        return jsonify({"error": "Missing date or doctor_svnr"}), 400
    
    db = get_db()
    
    # Get already booked slots for this doctor
    doctor_booked = db.get_doctor_booked_slots(int(doctor_svnr), date)
    
    # Get already booked slots for this patient (patient can't be in two places)
    patient_booked = []
    if patient_svnr:
        patient_booked = db.get_patient_booked_slots(int(patient_svnr), date)
    
    # Combine all unavailable slots
    unavailable_slots = set(doctor_booked + patient_booked)
    
    # Generate all possible time slots (8:00 - 17:00, every 30 minutes)
    all_slots = []
    for hour in range(8, 18):  # 8:00 to 17:00
        for minute in [0, 30]:
            if hour == 17 and minute == 30:
                continue  # Skip 17:30
            time_str = f"{hour:02d}:{minute:02d}"
            all_slots.append({
                "time": time_str,
                "available": time_str not in unavailable_slots
            })
    
    return jsonify({
        "date": date,
        "doctor_svnr": doctor_svnr,
        "patient_svnr": patient_svnr,
        "slots": all_slots
    })

@clerk_bp.route('/api/appointments', methods=['POST'])
def create_appointment():
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['patient_svnr', 'doctor_svnr', 'date', 'time']
    for field in required_fields:
        if not data.get(field):
            return jsonify({"success": False, "error": f"Fehlendes Feld: {field}"}), 400
    
    patient_svnr = data.get('patient_svnr')
    doctor_svnr = data.get('doctor_svnr')
    date = data.get('date')
    time = data.get('time')
    reason = data.get('reason', '')
    clerk_svnr = data.get('clerk_svnr', None)
    
    db = get_db()
    
    # Check for conflicts
    conflict = db.check_appointment_conflict(doctor_svnr, patient_svnr, date, time)
    if conflict:
        return jsonify({"success": False, "error": conflict["message"]}), 409
    
    try:
        # Create the appointment
        termin_id = db.create_appointment(
            patient_svnr=patient_svnr,
            doctor_svnr=doctor_svnr,
            date=date,
            time=time,
            reason=reason,
            clerk_svnr=clerk_svnr
        )
        
        return jsonify({
            "success": True,
            "termin_id": termin_id,
            "message": "Termin erfolgreich erstellt",
            "appointment": {
                "patient_svnr": patient_svnr,
                "doctor_svnr": doctor_svnr,
                "date": date,
                "time": time,
                "reason": reason
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@clerk_bp.route('/api/report/patient-visits')
def get_patient_visits_report():
    start_date = request.args.get('start_date', '2026-01-01')
    end_date = request.args.get('end_date', '2026-12-31')
    
    db = get_db()

    results = db.get_patients_doctor_visits(start_date, end_date)
    
    return jsonify({
        "start_date": start_date,
        "end_date": end_date,
        "results": results
    })