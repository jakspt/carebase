from flask import jsonify, request

from app.db import MongoDBStrategy, get_db, switch_to_mongo
from app.admin.data_gen import DataGenerator
from app.admin.db_migration import DataMigrator

from . import api_bp


# ── Status ────────────────────────────────────────────────────────────────────

@api_bp.route("/status")
def status():
    current_strategy = get_db()
    db_type = "MongoDB" if isinstance(current_strategy, MongoDBStrategy) else "MariaDB"
    return jsonify({"dbType": db_type})


# ── Admin ─────────────────────────────────────────────────────────────────────

@api_bp.route("/admin/seed", methods=["POST"])
def seed_db():
    try:
        data_generator = DataGenerator()
        data_generator.generate_all()
        return jsonify({"success": True, "message": "Database seeded successfully."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route("/admin/migrate", methods=["POST"])
def migrate_db():
    try:
        data_migrator = DataMigrator()
        data_migrator.migrate_all()
        switch_to_mongo()
        return jsonify({"success": True, "message": "Migration completed successfully."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ── Doctor — Use Case ─────────────────────────────────────────────────────────

@api_bp.route("/doctor/patients/search")
def search_patients():
    query = request.args.get("q", "")
    if not query:
        return jsonify({"patients": []})

    db = get_db()
    patients = db.find_patients(query)

    return jsonify({
        "patients": [
            {
                "id": str(p["id"]),
                "name": p["name"],
                "ssn": str(p["id"]),
                "insurance": p["insurance"],
            }
            for p in patients
        ]
    })


@api_bp.route("/doctor/patients/<patient_id>")
def get_patient_details(patient_id: str):
    db = get_db()
    patient = db.get_patient_details(patient_id)

    if not patient:
        return jsonify({"error": "Patient not found"}), 404

    appointments = [
        {
            "id": appt["id"],
            "date": str(appt["date"]),
            "time": str(appt["time"]),
            "doctorName": appt["doctor_name"],
            "reason": appt["reason"],
        }
        for appt in patient["appointments"]
    ]

    return jsonify({
        "id": str(patient["id"]),
        "name": patient["name"],
        "ssn": str(patient["id"]),
        "insurance": patient["insurance"],
        "appointments": appointments,
    })


@api_bp.route("/doctor/medications")
def get_medications():
    db = get_db()
    meds = db.get_all_meds()

    return jsonify({
        "medications": [
            {"id": m["id"], "name": m["name"]}
            for m in meds
        ]
    })


@api_bp.route(
    "/doctor/patients/<patient_id>/appointments/<int:appt_id>/treatments",
    methods=["POST"],
)
def add_treatment(patient_id: str, appt_id: int):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    description = data.get("description")
    cost = data.get("cost")
    medications = data.get("medications", [])

    if not description or cost is None:
        return jsonify({"error": "description and cost are required"}), 400

    db = get_db()

    # The DB strategy expects a list of dicts with id/name
    med_list = [{"id": m["id"], "name": m["name"]} for m in medications]

    success = db.add_treatment(patient_id, appt_id, description, float(cost), med_list)

    if success:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "error": "Failed to add treatment"}), 500


# ── Doctor — Report ───────────────────────────────────────────────────────────

@api_bp.route("/doctor/report")
def doctor_report():
    from datetime import datetime

    current_year = datetime.now().year
    selected_year = request.args.get("year", current_year, type=int)

    db = get_db()
    raw_data = db.get_doctor_report(selected_year)

    # Return the raw per-row data; let the frontend handle aggregation/charting
    data = [
        {
            "id": row["id"],
            "name": row["name"],
            "specialty": row["specialty"],
            "department": row["dept"],
            "year": row["year"],
            "totalCosts": float(row["total_costs"]),
        }
        for row in raw_data
    ]

    return jsonify({"year": selected_year, "data": data})


# ── Clerk — Use Case ──────────────────────────────────────────────────────────

@api_bp.route("/clerk/clerks/search")
def clerk_search_clerks():
    query = request.args.get("q", "").lower().strip()
    db = get_db()
    clerks = db.get_all_clerks()

    if query:
        filtered = [
            c for c in clerks
            if query in (c.get("name") or "").lower() or query in str(c.get("svnr", ""))
        ]
    else:
        filtered = clerks

    return jsonify({
        "clerks": [
            {
                "id": str(c["svnr"]),
                "name": c["name"],
                "ssn": str(c["svnr"]),
            }
            for c in filtered
        ]
    })


@api_bp.route("/clerk/patients/search")
def clerk_search_patients():
    query = request.args.get("q", "").lower().strip()
    if not query:
        return jsonify({"patients": []})

    db = get_db()
    patients = db.get_all_patients()

    filtered = [
        p for p in patients
        if query in (p.get("name") or "").lower() or query in str(p.get("svnr", ""))
    ]

    return jsonify({
        "patients": [
            {
                "id": str(p["svnr"]),
                "name": p["name"],
                "ssn": str(p["svnr"]),
                "insurance": p.get("versicherung", ""),
                "nacaScore": p.get("naca_score"),
            }
            for p in filtered
        ]
    })


@api_bp.route("/clerk/doctors")
def clerk_get_doctors():
    db = get_db()
    doctors = db.get_all_doctors()

    return jsonify({
        "doctors": [
            {
                "id": str(d["svnr"]),
                "name": d["name"],
                "ssn": str(d["svnr"]),
                "specialty": d.get("fachrichtung", ""),
                "position": d.get("position", ""),
                "department": d.get("abteilung", ""),
            }
            for d in doctors
        ]
    })


@api_bp.route("/clerk/time-slots")
def clerk_get_time_slots():
    raw_date = request.args.get("date", "")
    date = raw_date.strip().split("T")[0] if raw_date else ""
    doctor_ssn = request.args.get("doctorSsn") or request.args.get("doctor_svnr", "")
    patient_ssn = request.args.get("patientSsn") or request.args.get("patient_svnr", "")

    if not date or not doctor_ssn:
        return jsonify({"error": "Missing date or doctorSsn"}), 400

    db = get_db()
    doctor_booked = db.get_doctor_booked_slots(doctor_ssn, date)

    patient_booked = []
    if patient_ssn:
        patient_booked = db.get_patient_booked_slots(patient_ssn, date)

    unavailable_slots = set(doctor_booked + patient_booked)

    all_slots = []
    for hour in range(8, 18):  # 8:00 to 17:00
        for minute in [0, 30]:
            if hour == 17 and minute == 30:
                continue
            time_str = f"{hour:02d}:{minute:02d}"
            all_slots.append({
                "time": time_str,
                "available": time_str not in unavailable_slots,
            })

    return jsonify({
        "date": date,
        "doctorSsn": doctor_ssn,
        "patientSsn": patient_ssn,
        "slots": all_slots,
    })


@api_bp.route("/clerk/appointments", methods=["POST"])
def clerk_create_appointment():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "Request body is required"}), 400

    patient_ssn = data.get("patientSsn") or data.get("patient_svnr")
    doctor_ssn = data.get("doctorSsn") or data.get("doctor_svnr")
    raw_date = data.get("date")
    date = raw_date.strip().split("T")[0] if raw_date else None
    time = data.get("time")
    reason = data.get("reason", "")
    clerk_ssn = data.get("clerkSsn") or data.get("clerk_svnr")

    if not patient_ssn or not doctor_ssn or not date or not time:
        return jsonify({"success": False, "error": "Missing mandatory fields"}), 400

    db = get_db()
    conflict = db.check_appointment_conflict(doctor_ssn, patient_ssn, date, time)
    if conflict:
        return jsonify({"success": False, "error": conflict.get("message", "The selected time slot was already booked.")}), 409

    try:
        appointment_id = db.create_appointment(
            patient_svnr=patient_ssn,
            doctor_svnr=doctor_ssn,
            date=date,
            time=time,
            reason=reason,
            clerk_svnr=clerk_ssn,
        )

        return jsonify({
            "success": True,
            "appointmentId": appointment_id,
            "message": "Appointment successfully scheduled",
            "appointment": {
                "patientSsn": patient_ssn,
                "doctorSsn": doctor_ssn,
                "date": date,
                "time": time,
                "reason": reason,
            },
        })
    except Exception as e:
        err_msg = str(e).lower()
        if "duplicate" in err_msg or "unique" in err_msg or "1062" in err_msg:
            return jsonify({
                "success": False,
                "error": "The selected time slot was already booked by another user."
            }), 409
        return jsonify({"success": False, "error": str(e)}), 500


# ── Clerk — Report ────────────────────────────────────────────────────────────

@api_bp.route("/clerk/reports/patient-visits")
def clerk_patient_visits_report():
    start_date = request.args.get("startDate") or request.args.get("start_date") or "2026-01-01"
    end_date = request.args.get("endDate") or request.args.get("end_date") or "2026-12-31"

    if start_date > end_date:
        return jsonify({"error": "Start date must be earlier than or equal to end date"}), 400

    db = get_db()
    results = db.get_patients_doctor_visits(start_date, end_date)

    mapped_results = [
        {
            "patientSsn": str(r.get("patient_svnr", "")),
            "patientName": r.get("patient_name", ""),
            "insurance": r.get("versicherung", ""),
            "doctorSsn": str(r.get("arzt_svnr", "")),
            "doctorName": r.get("arzt_name", ""),
            "specialty": r.get("fachrichtung", ""),
            "department": r.get("abteilung") or r.get("fachrichtung", ""),
            "visitCount": int(r.get("anzahl_termine", 0)),
        }
        for r in results
    ]

    return jsonify({
        "startDate": start_date,
        "endDate": end_date,
        "results": mapped_results,
    })

