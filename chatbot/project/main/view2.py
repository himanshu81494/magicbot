from flask import render_template, Blueprint, request, json
from flask.ext.login import login_required

main_blueprint = Blueprint('main', __name__,)

def showusers():
  if not current_user.admin:
    return redirect('/')
  users = User.query.all()
  return render_template("main/Users.html", users=users)
