from flask import render_template
from . import doctor_bp


@doctor_bp.route('/')
def dashboard():
    return render_template('doctor/doctor.html')
