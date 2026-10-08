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
                "insurance": p.get("insurance", p.get("versicherung", "")),
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

    # Normalize the appointment data coming from the DB strategy
    appointments = []
    for appt in patient.get("appointments", patient.get("termine", [])):
        appointments.append({
            "id": appt.get("id", appt.get("termin_id")),
            "date": str(appt.get("date", appt.get("datum", ""))),
            "time": str(appt.get("time", appt.get("uhrzeit", ""))),
            "doctorName": appt.get("doctorName", appt.get("arzt_name", "")),
            "reason": appt.get("reason", appt.get("grund", "")),
        })

    return jsonify({
        "id": str(patient.get("id")),
        "name": patient.get("name"),
        "ssn": str(patient.get("id")),
        "insurance": patient.get("insurance", patient.get("versicherung", "")),
        "appointments": appointments,
    })


@api_bp.route("/doctor/medications")
def get_medications():
    db = get_db()
    meds = db.get_all_meds()

    return jsonify({
        "medications": [
            {"id": m.get("id", m.get("medikament_id")), "name": m.get("name", m.get("bezeichnung", ""))}
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
    data = []
    for row in raw_data:
        data.append({
            "id": row["id"],
            "name": row["name"],
            "specialty": row.get("specialty", row.get("fachrichtung", "")),
            "department": row.get("department", row.get("abteilung", "")),
            "year": row.get("year", row.get("jahr", selected_year)),
            "totalCosts": float(row.get("total_costs", row.get("gesamtkosten", 0))),
        })

    return jsonify({"year": selected_year, "data": data})
