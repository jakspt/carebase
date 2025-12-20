from flask import render_template

from . import admin_bp


# TODO: Implement
@admin_bp.route('/')
def overview():
    return render_template('admin/overview.html')


@admin_bp.route('/fill_db', methods=['POST'])
def fill_db():
    print('clearing db ...')
    print('filling db ...')
    # TODO: Implement DB filling
    return overview()


@admin_bp.route('/migrate_db', methods=['POST'])
def migrate_db():
    print('migrating db ...')
    print('now using Mongooo')
    # TODO: Implement DB migration
    return overview()
