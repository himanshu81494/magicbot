#################
#### imports ####
#################
from project import db, bcrypt

from flask import redirect
from flask_login import login_user, logout_user, \
  login_required, current_user
from flask import render_template, Blueprint, request, json
from flask_login import login_required
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
from project.models import User, fbUsers
import urllib, json

################
#### config ####
################

main_blueprint = Blueprint('main', __name__,)


################
#### routes ####
################
leveldata = [
    ['cg'],
    ['ty'],
    ['bd'],
    ['lt'],
    ['ct'],
    ['bgmn'],
    ['bgmx']
]
cityCode = [   ["hyderabad", 'ct:2060'],
    ["new delhi", 'ct:2624'],
    ["ahmedabad", 'ct:2690'],
    ["gurgoan", 'ct:2951'],
    ["bangalore", 'ct:3327'],
    ["mumbai", 'ct:4320'],
    ["navi mumbai", 'ct:4341'],
    ["pune", 'ct:4378'],
    ["kolkata", "ct:6903"],
    ["greater noida", "ct:7045"],
]
localityCode = {
    "ct:2060": [["miyapur","lt:80185"],["adibatla", "lt:85822"]],
    "ct:2624":[["subhash nagar", "lt:53514"],["sangam vihar", "lt:78193"]],
    "ct:2690":[["panchvati", "lt:54469"],["prahlad nagar", "lt:84435"]],
    "ct:2951":[["palam vihar", "lt:78710"],["sector 92", "lt:86514"]],
    "ct:3327":[["nelamangala", "lt:80455"],["sarjapur", "lt:80060"]],
    "ct:4320":[["bandra west", "lt:78839"],["malad west", "lt:80084"]],
    "ct:4341":[["ghansoli", "lt:60592"],["kharghar", "lt:78921"]],
    "ct:4378":[["kalyani nagar", "lt:82343"],["viman nagar", "lt:79726"]],
    "ct:6903":[["rajarhat", "lt:79304"],["thakur pukur", "lt:84834"]],
    "ct:7045":[["eta 2", "lt:98493"],["noida extension", "lt:93788"]]
}

VERIFY_TOKEN = ""
PAGE_ACCESS_TOKEN =   ""

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

@main_blueprint.route('/fb', methods=['GET', 'POST'])

def showfbusers():
  if fbUsers.query.filter_by(fbid=1).count() == 1:
    print 'yes 1'
  if fbUsers.query.filter_by(fbid=4).count() == 1:
    print 'yes 2'

  users = fbUsers.query.all()
  return render_template("main/fbUsers.html", users=users)

#///////////////////////////////////////////////////////////////////////////////////////////////////////////////
import utils as Util
@main_blueprint.route('/msg', methods=['GET'])
def message():
  return Util.returnMsg(), 200
import requests
@main_blueprint.route('/webhooks', methods=['GET'])
def verify():
  global VERIFY_TOKEN
  if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
    # if not request.args.get("hub.verify_token") == VERIFY_TOKEN os.environ["VERIFY_TOKEN"]:
    if not request.args.get("hub.verify_token") == VERIFY_TOKEN:
      return "Verification token mismatch", 403
    return request.args["hub.challenge"], 200
  return "Hello world", 200

@app.route('/webhooks', methods=['POST'])
def webhook():
  data = request.get_json()
  log(data)
  if data["object"] == "page":
    for entry in data["entry"]:
      for messaging_event in entry["messaging"]:
        if messaging_event.get("message"):
          message_text = ''
          sender_id = messaging_event["sender"]["id"]
          recipient_id = messaging_event["recipient"]["id"]
          user_data = Util.getFB(sender_id)

          if messaging_event["message"] and messaging_event["message"].get("text"):
            message_text = messaging_event["message"]["text"]

          if messaging_event["message"] and messaging_event["message"].get("quick_reply") and messaging_event["message"]["quick_reply"].get('payload'):
            PayL = (messaging_event["message"]["quick_reply"]["payload"])
            # print ("\n[[%s]]\n")%PayL
            if PayL.split(':')[0] ==  'ct':
              user = fbUsers.query.filter_by(fbid=sender_id).first()
              # u = user.state.split('%')
              print ("\n[[%s]]\n")%PayL
              if user and user.state:
                user.state = user.state + PayL + "%"
                db.session.commit()
              Send(sender_id, recipient_id, Util.MagicGenQuick(localityCode[PayL], 'select locality!', user_data))
            elif PayL.split(':')[0] ==  'lt':
              user = fbUsers.query.filter_by(fbid=sender_id).first()
              
              # u = user.state.split('%')
              s = ''
              if user and user.state:
                user.state = user.state + PayL + "%"
                db.session.commit()
                s = user.state
              s = '&'.join(('='.join(s.split(':'))).split('%'))[:-1]  
              URL = "http://hackathon.magicbricks.com:1208/property/mobileSearch?campCode=android&page=1&resultPerPage=4&searchType=1&"+s
              resp = requests.get(URL).json()
              # if user and user.state:
                # user.query.filter_by(id!=1).delete()
                # db.session.commit()
              # msg = "price: "+resp["result"][0]["price1"]+" Contact: "+resp['result'][0]['contact']+" City: "+resp["result"][0]["city"]
              if resp.get('result')
                D = resp['result'][0]
                TT = "Contact: "+D['contact']
              Send(sender_id, recipient_id, {"text" : TT})

              print("\n%s\n")%URL

              
          else:



            send_message(sender_id, recipient_id, message_text)
        # if messaging_event.get("delivery"): # delivery confirmation
        #   pass
        # if message_event.get("optin"): # optin confirmation
        #   pass
        elif messaging_event.get("postback"): # user clicked on postback\
          sender_id = messaging_event["sender"]["id"]
          recipient_id = messaging_event["recipient"]["id"]

          send_message_postback(sender_id, recipient_id, messaging_event["postback"]["payload"])
          # print("\n")
          # print(type(messaging_event["postback"]["payload"].encode('ascii','ignore')))
          # print("\n")

          
  return "OK", 200
import re
import random
def send_message_postback(sender_id, recipient_id, message_text):
  global leveldata
  Level = 0
  
  # print message_text
  user_data = Util.getFB(sender_id)
  if fbUsers.query.filter_by(fbid=sender_id).first() is None:
    db.session.add(fbUsers(
      fbid = sender_id,
      first_name = user_data['first_name'],
      last_name = user_data['last_name'],
      gender = user_data['gender'],
      locale = user_data['locale'],
      profile_pic = user_data['profile_pic'],
      timezone = user_data['timezone'],
      state = 'begin%'
      ))
    db.session.commit()
    messageData = {'text': 'welcome!'}
  else:
    user = fbUsers.query.filter_by(fbid=sender_id).first()
    State = user.state
    if State == 'begin%':
      user.state = message_text+'%'
      db.session.commit()
      messageData = Util.MagicGenMessage([['flat', 'ty:10002']], "select type", user_data)
    elif message_text.split(':')[0] == 'ty' and len(State.split('%'))-1 == 1:
      #messageData = {"text": "ty"}

      user = fbUsers.query.filter_by(fbid=sender_id).first()
      user.state = user.state+message_text+'%'
      db.session.commit()
      messageData = Util.MagicGenMessage([['bhk1', 'bd:1'], ['bhk2', 'bd:2'], ['bhk3', 'bd:3']], "select BHK", user_data)
    
    # elif message_text.split(':')[0] == 'ty' and len(State.split('%'))-1 == 2:
    #   messageData = Util.MagicGenMessage([['bhk1', 'bd:1'], ['bhk2', 'bd:2'], ['bhk3', 'bd:3']], "select BHK", user_data)
    #   user = fbUsers.query.filter_by(fbid=sender_id).first()
    #   user.state = user.state+message_text+'%'
    #   db.session.commit()
      
    elif message_text.split(':')[0] == 'bd' and len(State.split('%'))-1 == 2:
      # messageData = {"text": "enter city:"}
      user = fbUsers.query.filter_by(fbid=sender_id).first()
      user.state = user.state+message_text+'%'
      db.session.commit()
      messageData = Util.MagicGenQuick(cityCode, "select city", user_data)

      
    
    else:
      messageData = {"text" : "Type CANCEL to cancel!"}

        
    log(sender_id)
    log(user_data)
  

  # log("sending to {recipient}: {text}".format(recipient=sender_id, text=message_text))
  params = {
    "access_token": PAGE_ACCESS_TOKEN
  }
  headers = {
    "Content-Type": "application/json"
  }
  data = json.dumps({
    "recipient": {
      "id": sender_id
    },
    "message": messageData
  })

  Url = "https://graph.facebook.com/v2.6/me/messages"
  r = requests.post(Url, params=params, headers=headers, data=data)
  log(r.status_code)
  

def send_message(sender_id, recipient_id, message_text):
  user_data = Util.getFB(sender_id)
  if fbUsers.query.filter_by(fbid=sender_id) is None:
    db.session.add(fbUsers(
      fbid = sender_id,
      first_name = user_data['first_name'],
      last_name = user_data['last_name'],
      gender = user_data['gender'],
      locale = user_data['locale'],
      profile_pic = user_data['profile_pic'],
      timezone = user_data['timezone'],
      state = 'begin%'
      ))
    db.session.commit()
  # log(sender_id)
  # log(user_data)
  messageData = {}
  print "\n[%s]\n"%(message_text.lower()[:5])
  if message_text.lower()[:5] == 'wiki ':
    messageData = Util.WikiMessage(message_text.lower()[5:], user_data)
  elif message_text.lower() == 'magic':
    messageData = Util.MagicGenMessage([['buy', 'cg:S'],['rent', 'cg:R']], "I want to", user_data)
    print "\n[%s]\n"%(str(messageData))
  elif message_text.lower()[:7] == 'convert':
    areaValue = 0.0
    fromUnit = 'bigha'
    toUnit = 'are'
    li = message_text.lower().split() 
    pos = 0
    for i in range(len(li)):
      if li[i] == 'to' or li[i] == 'into' or li[i] == 'in':
        pos = i
    if pos > 0:
      areaValue = float(li[pos-2])
      fromUnit = li[pos-1]
      toUnit = li[pos+1]
    messageData = {'text': Convert(areaValue, fromUnit, toUnit)}

  elif message_text.lower() == 'payl':
    messageData = Util.MagicGenQuick([['buy', 'cg:S'],['rent', 'cg:R']], "I want to", user_data)
  else:
    messageData = Util.CustomFilter(message_text, user_data)
  # messageData = Util.CustomFilter(message_text, user_data)
  # messageData = {"text" : "lola"}

  # log("sending to {recipient}: {text}".format(recipient=sender_id, text=message_text))
  params = {
    "access_token": PAGE_ACCESS_TOKEN
  }
  headers = {
    "Content-Type": "application/json"
  }
  data = json.dumps({
    "recipient": {
      "id": sender_id
    },
    "message": messageData
  })

  Url = "https://graph.facebook.com/v2.6/me/messages"
  r = requests.post(Url, params=params, headers=headers, data=data)
  log(r.status_code)
  # if r.status_code != 200:
  #   log(r.text)
  #   log(r.status_code)
  #   log(r.reason)
  # return jsonify(result={"status": 200})


def Send(sender_id, recipient_id, messageData):
  user_data = Util.getFB(sender_id)
  if fbUsers.query.filter_by(fbid=sender_id) is None:
    db.session.add(fbUsers(
      fbid = sender_id,
      first_name = user_data['first_name'],
      last_name = user_data['last_name'],
      gender = user_data['gender'],
      locale = user_data['locale'],
      profile_pic = user_data['profile_pic'],
      timezone = user_data['timezone'],
      state = 'begin%'
      ))
    db.session.commit()
  # log(sender_id)
  # log(user_data)
  
  params = {
    "access_token": PAGE_ACCESS_TOKEN
  }
  headers = {
    "Content-Type": "application/json"
  }
  data = json.dumps({
    "recipient": {
      "id": sender_id
    },
    "message": messageData
  })

  Url = "https://graph.facebook.com/v2.6/me/messages"
  r = requests.post(Url, params=params, headers=headers, data=data)
  log(r.status_code)

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


from flask_mail import Message
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



def Convert(areaValue, fromUnit, toUnit):
  for i in range(len(reflist)):
    if reflist[i].lower() == fromUnit.lower():
      frompos = i
    elif reflist[i].lower() == toUnit.lower():
      topos = i
  first = float(mylist[frompos][topos].split(' ')[0])/100000
  second = 100000/float(mylist[topos][frompos].split(' ')[0])
  #print '1 ',reflist[frompos],'has ', first, reflist[topos]
  #print '1 ',reflist[frompos],'has ', second, reflist[topos]
  return ((max(first, second)+min(first, second))/2.000) * int(areaValue)
  #print '100000 ',reflist[frompos],'has ', mylist[frompos][topos]
  #print '100000 ',reflist[topos],'has ', mylist[topos][frompos]


reflist = [u'Sq-ft', u'Sq-m', u'Sq-yrd', u'Acre', u'Bigha', u'Hectare', u'Marla1', u'Kanal', u'Biswa1', u'Biswa2', u'Ground', u'Aankadam', u'Rood', u'Chatak', u'Kottah', u'Marla2', u'Cent', u'Perch', u'Guntha', u'Are']
mylist = [[u'100000.00 Sq-ft', u'9290.00 Sq-m', u'11111.11 Sq-yrd', u'2.29 Acre', u'3.71 Bigha', u'0.92 Hectare', u'367.29 Marla1', u'18.36 Kanal', u'0.02 Biswa1', u'0.01 Biswa2', u'3.87 Ground', u'129.04 Aankadam', u'0.85 Rood', u'20.64 Chatak', u'138.90 Kottah', u'1.72 Marla2', u'229.56 Cent', u'34.11 Perch', u'8.53 Guntha', u'8.63 Are'],
[u'1076426.26 Sq-ft', u'100000.00 Sq-m', u'119602.91 Sq-yrd', u'24.71 Acre', u'40.00 Bigha', u'10.00 Hectare', u'3953.66 Marla1', u'197.68 Kanal', u'0.28 Biswa1', u'0.18 Biswa2', u'41.66 Ground', u'1389.10 Aankadam', u'9.18 Rood', u'222.22 Chatak', u'1495.21 Kottah', u'18.52 Marla2', u'2471.08 Cent', u'367.24 Perch', u'91.83 Guntha', u'92.93 Are'],
[u'900000.00 Sq-ft', u'83610.00 Sq-m', u'100000.00 Sq-yrd', u'20.66 Acre', u'33.44 Bigha', u'8.36 Hectare', u'3305.65 Marla1', u'165.28 Kanal', u'0.23 Biswa1', u'0.15 Biswa2', u'34.83 Ground', u'1161.42 Aankadam', u'7.67 Rood', u'185.80 Chatak', u'1250.14 Kottah', u'15.48 Marla2', u'2066.07 Cent', u'307.05 Perch', u'76.78 Guntha', u'77.70 Are'],
[u'4356081808.39 Sq-ft', u'404680000.00 Sq-m', u'484009089.82 Sq-yrd', u'100000.00 Acre', u'161872.00 Bigha', u'40468.00 Hectare', u'15999683.70 Marla1', u'799984.18 Kanal', u'1161.27 Biswa1', u'743.21 Biswa2', u'168623.69 Ground', u'5621414.38 Aankadam', u'37153.87 Rood', u'899308.87 Chatak', u'6050837.32 Kottah', u'74951.84 Marla2', u'10000000.00 Cent', u'1486154.97 Perch', u'371641.10 Guntha', u'376096.65 Are'],
[u'2691065662.00 Sq-ft', u'250000000.00 Sq-m', u'299007295.77 Sq-yrd', u'61777.20 Acre', u'100000.00 Bigha', u'25000.00 Hectare', u'9884157.67 Marla1', u'494207.88 Kanal', u'717.40 Biswa1', u'459.13 Biswa2', u'104171.00 Ground', u'3472752.78 Aankadam', u'22952.62 Rood', u'555567.90 Chatak', u'3738038.27 Kottah', u'46303.15 Marla2', u'6177720.66 Cent', u'918105.03 Perch', u'229589.49 Guntha', u'232342.00 Are'],
[u'10764262648.00 Sq-ft', u'1000000000.00 Sq-m', u'1196029183.11 Sq-yrd', u'247108.82 Acre', u'400000.00 Bigha', u'100000.00 Hectare', u'39536630.68 Marla1', u'1976831.53 Kanal', u'2869.60 Biswa1', u'1836.55 Biswa2', u'416684.02 Ground', u'13891011.12 Aankadam', u'91810.50 Rood', u'2222271.60 Chatak', u'14952153.11 Kottah', u'185212.62 Marla2', u'24710882.67 Cent', u'3672420.12 Perch', u'918357.97 Guntha', u'929368.02 Are'],
[u'27226049.51 Sq-ft', u'2529300.00 Sq-m', u'3025116.61 Sq-yrd', u'625.01 Acre', u'1011.72 Bigha', u'252.93 Hectare', u'100000.00 Marla1', u'5000.00 Kanal', u'7.25 Biswa1', u'4.64 Biswa2', u'1053.91 Ground', u'35134.53 Aankadam', u'232.21 Rood', u'5620.79 Chatak', u'37818.48 Kottah', u'468.45 Marla2', u'62501.23 Cent', u'9288.65 Perch', u'2322.80 Guntha', u'2350.65 Are'],
[u'544520990.31 Sq-ft', u'50586000.00 Sq-m', u'60502332.25 Sq-yrd', u'12500.24 Acre', u'20234.40 Bigha', u'5058.60 Hectare', u'2000000.00 Marla1', u'100000.00 Kanal', u'145.16 Biswa1', u'92.90 Biswa2', u'21078.37 Ground', u'702690.68 Aankadam', u'4644.32 Rood', u'112415.83 Chatak', u'756369.61 Kottah', u'9369.16 Marla2', u'1250024.71 Cent', u'185773.04 Perch', u'46456.05 Guntha', u'47013.01 Are'],
[u'375113024757.80 Sq-ft', u'34848000000.00 Sq-m', u'41679224973.08 Sq-yrd', u'8611248.39 Acre', u'13939200.00 Bigha', u'3484800.00 Hectare', u'1377772506.22 Marla1', u'68888625.31 Kanal', u'100000.00 Biswa1', u'64000.11 Biswa2', u'14520605.02 Ground', u'484073955.74 Aankadam', u'3199412.41 Rood', u'77441720.92 Chatak', u'521052631.57 Kottah', u'6454289.52 Marla2', u'861124839.37 Cent', u'127976496.51 Perch', u'32002938.74 Guntha', u'32386617.10 Are'],
[u'586113024757.80 Sq-ft', u'54449900000.00 Sq-m', u'65123669417.53 Sq-yrd', u'13455050.90 Acre', u'21779960.00 Bigha', u'5444990.00 Hectare', u'2152765587.31 Marla1', u'107638279.36 Kanal', u'156249.71 Biswa1', u'100000.00 Biswa2', u'22688403.68 Ground', u'756364166.74 Aankadam', u'4999072.71 Rood', u'121002466.72 Chatak', u'814143241.62 Kottah', u'10084808.86 Marla2', u'1345505090.44 Cent', u'199962908.55 Perch', u'50004499.95 Guntha', u'50603996.28 Are'],
[u'2583315392.89 Sq-ft', u'239990000.00 Sq-m', u'287035043.65 Sq-yrd', u'59303.64 Acre', u'95996.00 Bigha', u'23999.00 Hectare', u'9488395.99 Marla1', u'474419.79 Kanal', u'688.67 Biswa1', u'440.75 Biswa2', u'100000.00 Ground', u'3333703.76 Aankadam', u'22033.60 Rood', u'533322.96 Chatak', u'3588367.22 Kottah', u'44449.17 Marla2', u'5930364.73 Cent', u'881344.10 Perch', u'220396.73 Guntha', u'223039.03 Are'],
[u'77490850.37 Sq-ft', u'7198900.00 Sq-m', u'8610094.48 Sq-yrd', u'1778.91 Acre', u'2879.56 Bigha', u'719.89 Hectare', u'284620.25 Marla1', u'14231.01 Kanal', u'20.65 Biswa1', u'13.22 Biswa2', u'2999.66 Ground', u'100000.00 Aankadam', u'660.93 Rood', u'15997.91 Chatak', u'107639.05 Kottah', u'1333.32 Marla2', u'177891.17 Cent', u'26437.38 Perch', u'6611.16 Guntha', u'6690.42 Are'],
[u'11724434876.21 Sq-ft', u'1089200000.00 Sq-m', u'1302714986.24 Sq-yrd', u'269150.93 Acre', u'435680.00 Bigha', u'108920.00 Hectare', u'43063298.14 Marla1', u'2153164.90 Kanal', u'3125.57 Biswa1', u'2000.37 Biswa2', u'453852.24 Ground', u'15130089.31 Aankadam', u'100000.00 Rood', u'2420498.23 Chatak', u'16285885.16 Kottah', u'201733.59 Marla2', u'26915093.40 Cent', u'4000000.00 Perch', u'1000275.50 Guntha', u'1012267.65 Are'],
[u'484381054.89 Sq-ft', u'44999000.00 Sq-m', u'53820117.21 Sq-yrd', u'11119.65 Acre', u'17999.60 Bigha', u'4499.90 Hectare', u'1779108.84 Marla1', u'88955.44 Kanal', u'129.12 Biswa1', u'82.64 Biswa2', u'18750.36 Ground', u'625081.60 Aankadam', u'4131.38 Rood', u'100000.00 Chatak', u'672831.93 Kottah', u'8334.38 Marla2', u'1111965.00 Cent', u'165255.23 Perch', u'41325.19 Guntha', u'41820.63 Are'],
[u'71991388.58 Sq-ft', u'6688000.00 Sq-m', u'7999043.17 Sq-yrd', u'1652.66 Acre', u'2675.20 Bigha', u'668.80 Hectare', u'264420.98 Marla1', u'13221.04 Kanal', u'19.19 Biswa1', u'12.28 Biswa2', u'2786.78 Ground', u'92903.08 Aankadam', u'614.02 Rood', u'14862.55 Chatak', u'100000.00 Kottah', u'1238.70 Marla2', u'165266.38 Cent', u'24561.14 Perch', u'6141.97 Guntha', u'6215.61 Are'],
[u'5811840688.91 Sq-ft', u'539920000.00 Sq-m', u'645760076.54 Sq-yrd', u'133418.99 Acre', u'215968.00 Bigha', u'53992.00 Hectare', u'21346617.64 Marla1', u'1067330.88 Kanal', u'1549.35 Biswa1', u'991.59 Biswa2', u'224976.04 Ground', u'7500034.72 Aankadam', u'49570.32 Rood', u'1199848.88 Chatak', u'8072966.50 Kottah', u'100000.00 Marla2', u'13341899.77 Cent', u'1982813.07 Perch', u'495839.83 Guntha', u'501784.38 Are'],
[u'43560818.08 Sq-ft', u'4046800.00 Sq-m', u'4840090.89 Sq-yrd', u'1000.00 Acre', u'1618.72 Bigha', u'404.68 Hectare', u'159996.83 Marla1', u'7999.84 Kanal', u'11.61 Biswa1', u'7.43 Biswa2', u'1686.23 Ground', u'56214.14 Aankadam', u'371.53 Rood', u'8993.08 Chatak', u'60508.37 Kottah', u'749.51 Marla2', u'100000.00 Cent', u'14861.54 Perch', u'3716.41 Guntha', u'3760.96 Are'],
[u'293110871.90 Sq-ft', u'27230000.00 Sq-m', u'32567874.65 Sq-yrd', u'6728.77 Acre', u'10892.00 Bigha', u'2723.00 Hectare', u'1076582.45 Marla1', u'53829.12 Kanal', u'78.13 Biswa1', u'50.00 Biswa2', u'11346.30 Ground', u'378252.23 Aankadam', u'2500.00 Rood', u'60512.45 Chatak', u'407147.12 Kottah', u'5043.33 Marla2', u'672877.33 Cent', u'100000.00 Perch', u'25006.88 Guntha', u'25306.69 Are'],
[u'1172120559.74 Sq-ft', u'108890000.00 Sq-m', u'130235617.74 Sq-yrd', u'26907.68 Acre', u'43556.00 Bigha', u'10889.00 Hectare', u'4305143.71 Marla1', u'215257.18 Kanal', u'312.47 Biswa1', u'199.98 Biswa2', u'45372.72 Ground', u'1512592.20 Aankadam', u'9997.24 Rood', u'241983.15 Chatak', u'1628139.95 Kottah', u'20167.80 Marla2', u'2690768.01 Cent', u'399889.82 Perch', u'100000.00 Guntha', u'101198.88 Are'],
[u'1158234660.92 Sq-ft', u'107600000.00 Sq-m', u'128692740.10 Sq-yrd', u'26588.90 Acre', u'43040.00 Bigha', u'10760.00 Hectare', u'4254141.46 Marla1', u'212707.07 Kanal', u'308.76 Biswa1', u'197.61 Biswa2', u'44835.20 Ground', u'1494672.79 Aankadam', u'9878.81 Rood', u'239116.42 Chatak', u'1608851.67 Kottah', u'19928.87 Marla2', u'2658890.97 Cent', u'395152.40 Perch', u'98815.31 Guntha', u'100000.00 Are']]
