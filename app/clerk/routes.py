from flask import render_template, request, jsonify

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
    

# API Endpoints with example data

@clerk_bp.route('/api/patients/search')
def search_patients():
    """Search patients by name or SVNr - returns example data"""
    query = request.args.get('q', '').lower()
    
    # Example patient data
    example_patients = [
        {"svnr": "1234567890", "name": "Max Mustermann", "versicherung": "ÖGK"},
        {"svnr": "2345678901", "name": "Maria Musterfrau", "versicherung": "SVS"},
        {"svnr": "3456789012", "name": "Hans Huber", "versicherung": "BVAEB"},
        {"svnr": "4567890123", "name": "Anna Schmidt", "versicherung": "ÖGK"},
        {"svnr": "5678901234", "name": "Peter Maier", "versicherung": "SVS"},
        {"svnr": "6789012345", "name": "Julia Wagner", "versicherung": "ÖGK"},
        {"svnr": "7890123456", "name": "Thomas Gruber", "versicherung": "BVAEB"},
        {"svnr": "8901234567", "name": "Sarah Fischer", "versicherung": "ÖGK"},
    ]
    
    # Filter based on query
    filtered = [
        p for p in example_patients 
        if query in p['name'].lower() or query in p['svnr']
    ]
    
    return jsonify({"patients": filtered})


@clerk_bp.route('/api/timeslots')
def get_timeslots():
    """Get available time slots for a given date - returns example data"""
    date = request.args.get('date', '')
    
    # Example time slots (some available, some not)
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
    
    return jsonify({"date": date, "slots": example_slots})


@clerk_bp.route('/api/doctors')
def get_doctors():
    """Get available doctors for a given date and time - returns example data"""
    date = request.args.get('date', '')
    time = request.args.get('time', '')
    
    # Example doctor data
    example_doctors = [
        {
            "svnr": "D123456789",
            "name": "Dr. Elisabeth Berger",
            "fachrichtung": "Allgemeinmedizin",
            "position": "Oberärztin",
            "abteilung": "Innere Medizin"
        },
        {
            "svnr": "D234567890",
            "name": "Dr. Michael Hofer",
            "fachrichtung": "Kardiologie",
            "position": "Facharzt",
            "abteilung": "Kardiologie"
        },
        {
            "svnr": "D345678901",
            "name": "Dr. Sandra Pichler",
            "fachrichtung": "Orthopädie",
            "position": "Oberärztin",
            "abteilung": "Orthopädie"
        },
        {
            "svnr": "D456789012",
            "name": "Dr. Andreas Steiner",
            "fachrichtung": "Neurologie",
            "position": "Facharzt",
            "abteilung": "Neurologie"
        },
        {
            "svnr": "D567890123",
            "name": "Dr. Claudia Winkler",
            "fachrichtung": "Dermatologie",
            "position": "Oberärztin",
            "abteilung": "Dermatologie"
        },
    ]
    
    return jsonify({"date": date, "time": time, "doctors": example_doctors})


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
    return jsonify({
        "success": True,
        "termin_id": 12345,
        "message": "Termin erfolgreich erstellt",
        "appointment": {
            "patient_svnr": data.get('patient_svnr'),
            "doctor_svnr": data.get('doctor_svnr'),
            "date": data.get('date'),
            "time": data.get('time'),
            "reason": data.get('reason')
        }
    })