from flask import render_template
from . import doctor_bp


# TODO: Implement
@doctor_bp.route('/')
def overview():
    return render_template('doctor/overview.html')
