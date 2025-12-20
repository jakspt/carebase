from flask import render_template

from . import admin_bp


# TODO: Implement
@admin_bp.route('/')
def overview():
    return render_template('admin/overview.html')
