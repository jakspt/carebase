from flask import abort, redirect, render_template, session, url_for

from . import core_bp


@core_bp.route("/")
def index():
    # TODO: Implement so that depending on the current user, it shows their homepage
    if "user" in session:
        return redirect_to_overview()
    return render_template("index.html")


@core_bp.route("/login/<user>")
def login(user):
    match str.lower(user):
        case "admin":
            session["user"] = "admin"
            return redirect_to_overview()
        case "clerk":
            session["user"] = "clerk"
            return redirect_to_overview()
        case "doctor":
            session["user"] = "doctor"
            return redirect_to_overview()
        case _:
            abort(400)


def redirect_to_overview():
    assert "user" in session, "User not logged in"
    return redirect(url_for(session["user"] + ".overview"))


# Take users back to the landing page
@core_bp.route("/logout")
def logout():
    session.pop("user", None)
    return index()
