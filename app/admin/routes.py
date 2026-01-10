from flask import render_template

from app.db import switch_to_mongo

from . import admin_bp
from .data_gen import DataGenerator
from .db_migration import DataMigrator


@admin_bp.route("/")
def overview():
    return render_template("admin/overview.html")


@admin_bp.route("/fill_db", methods=["POST"])
def fill_db():
    data_generator = DataGenerator()
    data_generator.generate_all()
    return overview()


@admin_bp.route("/migrate_db", methods=["POST"])
def migrate_db():
    data_migrator = DataMigrator()
    data_migrator.migrate_all()
    switch_to_mongo()
    return overview()
