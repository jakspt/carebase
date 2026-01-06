from flask import render_template

from . import clerk_bp


# TODO: Implement
@clerk_bp.route('/')
def overview():
    return render_template('clerk/overview.html')

@clerk_bp.route('/appointment')
def appointment():
    return render_template('clerk/appointment.html')


@clerk_bp.route('/report')
def report():
    return render_template('clerk/report.html')