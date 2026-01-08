from flask import render_template, request, jsonify

from . import clerk_bp

from app.db import *

@clerk_bp.route('/')
def overview():
    return render_template('clerk/overview.html')


@clerk_bp.route('/appointment')
def appointment():
    return render_template('clerk/appointment.html')


@clerk_bp.route('/report')
def report():
    return render_template('clerk/report.html')
    

# API Endpoints with example data

@clerk_bp.route('/api/patients/search')
def search_patients():
    """Search patients by name or SVNr - returns example data"""
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
    """Get all doctors - used to populate departments and doctor selection"""
    
    db = get_db()

    doctors = db.get_all_doctors()
    
    return jsonify({"doctors": doctors})

@clerk_bp.route('/api/timeslots')
def get_timeslots():
    """Get available time slots for a given date and doctor"""
    date = request.args.get('date', '')
    doctor_svnr = request.args.get('doctor_svnr', '')
    
    # Example time slots - availability varies based on date/doctor
    # In a real implementation, this would check the database for existing appointments
    example_slots = [
        {"time": "08:00", "available": True},
        {"time": "08:30", "available": True},
        {"time": "09:00", "available": False},
        {"time": "09:30", "available": True},
        {"time": "10:00", "available": True},
        {"time": "10:30", "available": False},
        {"time": "11:00", "available": True},
        {"time": "11:30", "available": True},
        {"time": "12:00", "available": False},
        {"time": "13:00", "available": True},
        {"time": "13:30", "available": True},
        {"time": "14:00", "available": True},
        {"time": "14:30", "available": False},
        {"time": "15:00", "available": True},
        {"time": "15:30", "available": True},
        {"time": "16:00", "available": True},
        {"time": "16:30", "available": False},
        {"time": "17:00", "available": True},
    ]
    
    return jsonify({
        "date": date,
        "doctor_svnr": doctor_svnr,
        "slots": example_slots
    })

@clerk_bp.route('/api/appointments', methods=['POST'])
def create_appointment():
    """Create a new appointment - returns example success response"""
    data = request.get_json()
    
    # In a real implementation, you would:
    # 1. Validate the data
    # 2. Check for conflicts
    # 3. Insert into database
    # 4. Return the created appointment ID
    
    # Example success response
    import random
    termin_id = random.randint(10000, 99999)
    
    return jsonify({
        "success": True,
        "termin_id": termin_id,
        "message": "Termin erfolgreich erstellt",
        "appointment": {
            "patient_svnr": data.get('patient_svnr'),
            "doctor_svnr": data.get('doctor_svnr'),
            "date": data.get('date'),
            "time": data.get('time'),
            "reason": data.get('reason')
        }
    })


@clerk_bp.route('/api/report/patient-visits')
def get_patient_visits_report():
    """Get patient visits per doctor within a date range - implements the complex query"""
    start_date = request.args.get('start_date', '2024-01-01')
    end_date = request.args.get('end_date', '2024-12-31')
    
    # Example data matching the query structure:
    # SELECT Patient_SVNr, Patient_Name, Versicherungsträger, 
    #        Arzt_SVNr, Arzt_Name, Fachrichtung, COUNT(TerminID) AS Anzahl_Termine
    # FROM Termin JOIN Patient JOIN Arzt ...
    # WHERE Datum BETWEEN start_date AND end_date
    # GROUP BY Patient_SVNr, Arzt_SVNr
    
    example_results = [
        {
            "patient_svnr": "1234567890",
            "patient_name": "Max Mustermann",
            "versicherungstraeger": "ÖGK",
            "arzt_svnr": "D123456789",
            "arzt_name": "Dr. Elisabeth Berger",
            "fachrichtung": "Allgemeinmedizin",
            "anzahl_termine": 5
        },
        {
            "patient_svnr": "1234567890",
            "patient_name": "Max Mustermann",
            "versicherungstraeger": "ÖGK",
            "arzt_svnr": "D234567890",
            "arzt_name": "Dr. Michael Hofer",
            "fachrichtung": "Kardiologie",
            "anzahl_termine": 2
        },
        {
            "patient_svnr": "2345678901",
            "patient_name": "Maria Musterfrau",
            "versicherungstraeger": "SVS",
            "arzt_svnr": "D123456789",
            "arzt_name": "Dr. Elisabeth Berger",
            "fachrichtung": "Allgemeinmedizin",
            "anzahl_termine": 3
        },
        {
            "patient_svnr": "2345678901",
            "patient_name": "Maria Musterfrau",
            "versicherungstraeger": "SVS",
            "arzt_svnr": "D345678901",
            "arzt_name": "Dr. Sandra Pichler",
            "fachrichtung": "Orthopädie",
            "anzahl_termine": 4
        },
        {
            "patient_svnr": "3456789012",
            "patient_name": "Hans Huber",
            "versicherungstraeger": "BVAEB",
            "arzt_svnr": "D456789012",
            "arzt_name": "Dr. Andreas Steiner",
            "fachrichtung": "Neurologie",
            "anzahl_termine": 1
        },
        {
            "patient_svnr": "4567890123",
            "patient_name": "Anna Schmidt",
            "versicherungstraeger": "ÖGK",
            "arzt_svnr": "D234567890",
            "arzt_name": "Dr. Michael Hofer",
            "fachrichtung": "Kardiologie",
            "anzahl_termine": 6
        },
        {
            "patient_svnr": "5678901234",
            "patient_name": "Peter Maier",
            "versicherungstraeger": "SVS",
            "arzt_svnr": "D567890123",
            "arzt_name": "Dr. Claudia Winkler",
            "fachrichtung": "Dermatologie",
            "anzahl_termine": 2
        },
        {
            "patient_svnr": "6789012345",
            "patient_name": "Julia Wagner",
            "versicherungstraeger": "ÖGK",
            "arzt_svnr": "D123456789",
            "arzt_name": "Dr. Elisabeth Berger",
            "fachrichtung": "Allgemeinmedizin",
            "anzahl_termine": 4
        },
    ]
    
    return jsonify({
        "start_date": start_date,
        "end_date": end_date,
        "results": example_results
    })