from flask import render_template

from . import clerk_bp


# TODO: Implement
@clerk_bp.route('/')
def overview():
    return render_template('clerk/overview.html')
