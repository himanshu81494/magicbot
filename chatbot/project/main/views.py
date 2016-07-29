# project/main/views.py


#################
#### imports ####
#################
from project import db, bcrypt

from flask import redirect
from flask.ext.login import login_user, logout_user, \
  login_required, current_user
from flask import render_template, Blueprint, request, json
from flask.ext.login import login_required
from project.models import User
from werkzeug.security import generate_password_hash, \
     check_password_hash

from werkzeug.security import generate_password_hash, check_password_hash

from flask_wtf import Form
from wtforms import validators
from wtforms import TextField, StringField, SelectField
from wtforms.validators import required
from project import app, db
from flask import redirect, url_for, request, flash
from project.models import User
import urllib, json

################
#### config ####
################

main_blueprint = Blueprint('main', __name__,)


################
#### routes ####
################
VERIFY_TOKEN = "MAGIC_BOT_VERIFY_TOKEN"
PAGE_ACCESS_TOKEN =   "EAANUyQ4rT6MBAHUXyzN8ZArXODjA9BtCVS8PaQ81P8BQVcDeh5ibYr7POk0WeCDvuoZBUUYZCa8yKPJkxEZCLtV9ajdNBZCuB5ePWHJBe0uTACZCTl7Al5LFsmnwTdvxMFykmriVlfKAGpvpnYDfMH6eqdowvmLxswKradGcMT5gZDZD"
@main_blueprint.route('/')
@login_required
def home():
    return render_template('main/index.html')

@main_blueprint.route('/showusers', methods=['GET', 'POST'])
@login_required
def showusers():
  if not current_user.admin:
    return redirect('/')
  users = User.query.all()
  return render_template("main/Users.html", users=users)
#///////////////////////////////////////////////////////////////////////////////////////////////////////////////
import requests
@main_blueprint.route('/', methods=['GET'])
def verify():
  if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
    # if not request.args.get("hub.verify_token") == VERIFY_TOKEN os.environ["VERIFY_TOKEN"]:
    if not request.args.get("hub.verify_token") == VERIFY_TOKEN:

      return "Verification token mismatch", 403
    return request.args["hub.challenge"], 200
  return "Hello world", 200
@app.route('/', methods=['POST'])
def webhook():
  data = request.get_json()
  log(data)
  if data["object"] == "page":
    for entry in data["entry"]:
      for messaging_event in entry["messaging"]:
        if messaging_event.get("message"):

          sender_id = messaging_event["sender"]["id"]
          recipient_id = messaging_event["recipient"]["id"]
          message_text = messaging_event["message"]["text"]

          send_message(sender_id, "Recieved: {msg}".format(msg=message_text))
        if messaging_event.get("delivery"): # delivery confirmation
          pass
        if message_event.get("optin"): # optin confirmation
          pass
        if messaging_event("postback"): # user clicked on postback
          pass
  return "OK", 200

def send_message(recipient_id, message_text):
  # log("sending to {recipient}: {text}".format(recipient=recipient_id, text=message_text))
  params = {
    "access_token": PAGE_ACCESS_TOKEN#os.environ["PAGE_ACCESS_TOKEN"]
  }
  headers = {
    "Content-Type": "application/json"
  }
  data = json.dumps({
    "recipient": {
      "id": recipient_id
    },
    "message":{
      "text": message_text
    }
  })
  Url = "https://graph.facebook.com/v2.6/me/messages"
  r = requests.post(Url, params=params, headers=headers, data=data)
  if r.status_code != 200:
    log(r.status_code)
    log(r.text)

def log(message):
  print str(message)


@main_blueprint.route('/api/weather', methods=['GET', 'POST'])
def weather():
  api_key = "f3d7d2bc7eef02d1a59d6217dc182120"
  key = "ece6f8d5e3dbdc4c" #key for wunder api
  # Key = "3jPE7vUz4u0MmQU7nnenBbdEdpxtbqqn" #accuweathe
  # http://api.accuweather.com/locations/v1/search?apikey=3jPE7vUz4u0MmQU7nnenBbdEdpxtbqqn&q=san
  if True: #request.headers['Content-Type'] == 'application/json':
    # lat = request.json['lat']
    # lon = request.json['lon']

    city = request.args.get('city')
    #url = "http://api.openweathermap.org/data/2.5/weather?lat="+ lat +"&lon="+ lon +"&appid=" + api_key
    url = "http://api.openweathermap.org/data/2.5/weather?units=metric&q="+ city +"&appid=" + api_key
    print url
    response = urllib.urlopen(url)
    data = json.loads(response.read())
    resp = {}
    if data['cod'] == 200:
      resp['response'] = "success"
      resp['word'] = data['weather'][0]['main']
      resp['icon'] = data['weather'][0]['icon']
      resp['temp'] = data['main']['temp']
      resp['humi'] = data['main']['humidity']

      return json.dumps(resp)
    else:
      resp['response'] = "failure"
      return json.dumps(resp)

from math import radians, cos, sin, asin, sqrt
def dis(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    km = 6367 * c
    return km

@main_blueprint.route('/pushnotif', methods=['GET', 'POST'])
def pushnotif():
  if current_user.admin:
    impact = request.args.get('impact')
    precaution = request.args.get('precaution')
    serverlat = request.args.get('serverlat')
    serverlon = request.args.get('serverlon')
    users = User.query.all()
    for user in users:
      if user.longitude and user.latitude and serverlon and serverlat:
        current_dis = dis(float(user.longitude), float(user.latitude), float(serverlon), float(serverlat))
        # flash(current_user, "warning")
       
        if current_dis < float(impact):
          user.threat = True
          user.precaution = precaution
          db.session.commit()
  return render_template('main/push.html')

@main_blueprint.route('/api/pushnotif', methods=['GET', 'POST'])
def apipushnotif():
  if request.headers['Content-Type'] == 'application/json':
    user = User.query.filter_by(user_token = request.json['token']).first()
    if user:
      data = {}
      if user.threat:
        data['response'] = 1
        data['precaution'] = user.precaution
        return json.dumps(data)
      else:
        data['response'] = 0
        return json.dumps(data)


from flask.ext.mail import Message
from project import app, mail

@main_blueprint.route('/api/emergency', methods=['GET', 'POST'])
def emergency():
  if request.headers['Content-Type'] == 'application/json':
    user = User.query.filter_by(user_token = request.json['token']).first()
    # user = User.query.first()
    data = {}
    if user:
      lat = request.json['lat']
      lon = request.json['lon']
      if lat and lon:
        listo = user.contacts.split(',')
        # listo = "me@himanshugautam.com, himanshu81494@gmail.com".split(', ')
        subject = "Hi,"+user.email+"is in danger"
        template = "<a href='https://www.google.co.in/maps/@%s,%s,15z' >Locate %s!</a>"%(lat, lon, user.email)
        msg = Message(
        subject,
        recipients=listo,
        html=template,
        sender=app.config['MAIL_DEFAULT_SENDER']
        )
        if mail.send(msg):
          data['response'] = "success"
          return json.dumps(data)
    else:
      data['response'] = "failure"
      return json.dumps(data)

@main_blueprint.route('/api/toggle', methods=['GET', 'POST'])
def toggle():
  if request.args.get('undo'):
    user = User.query.all()
    for u in user:
      u.threat = False
      u.precaution = ''
    db.session.commit()
    return redirect('/pushnotif')

import httplib
@main_blueprint.route('/api/gcm', methods=['GET', 'POST'])
def gcm():
  data = {}
  if request.headers['Content-Type'] == 'application/json':
    user = User.query.filter_by(user_token = request.json['token']).first()
    if user :

      user.gcmregid = request.json['regId']
      user.gcmapikey = request.json['api_key']
      db.session.commit()
      data['response'] = "success"
      return json.dumps(data)
    else:
      data['response'] = "failure"
      return json.dumps(data)

