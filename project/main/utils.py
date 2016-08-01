
import re
import random
import requests
PAGE_ACCESS_TOKEN =   "EAANZAbOErD3cBAIPPCfcScZAIsXY8JsPILWKXqpAlJvzmGAZBkg2BqW1ZBWvLF0WQmx43ZAO7FjYsRx0iEorvlORU7KQS4k9lC5mFFkOZC81JI3wFz6k4SbILhW5ipi8VZCPiBhqK27Ah2aN89poPvKqjKkBSO4G7gc0Xzq5g2WvQZDZD"

jokes = {
         'stupid': ["""Yo' Mama is so stupid, she needs a recipe to make ice cubes.""",
                    """Yo' Mama is so stupid, she thinks DNA is the National Dyslexics Association."""],
         'fat':    ["""Yo' Mama is so fat, when she goes to a restaurant, instead of a menu, she gets an estimate.""",
                    """ Yo' Mama is so fat, when the cops see her on a street corner, they yell, "Hey you guys, break it up!" """],
         'dumb':   ["""Yo' Mama is so dumb, when God was giving out brains, she thought they were milkshakes and asked for extra thick.""",
                    """Yo' Mama is so dumb, she locked her keys inside her motorcycle."""],
                    'hi':     ["""Hello!"""],
          'kem cho':  ["""Majama!"""],
          'hello':   ["""Hello, I am MagicBricks chatbot."""] 
         }
import bot as Bot
def CustomFilter(input_message, user_data):
  global jokes
  if input_message == '':
    return {"text": 'None'}
  # msg = "Recieved: {msg}".format(msg=input_message)
  # tokens = re.sub(r"[^a-zA-Z0-9\s]",' ',input_message).lower().split()
  # joke_text = ''
  # for token in tokens:
  #   if token in jokes:
  #     joke_text = random.choice(jokes[token])
  #     break
  # if not joke_text:
  #     joke_text = "I didn't understand! Send 'stupid', 'fat', 'dumb' for a Yo Mama joke!"
  Text= Bot.get_response(input_message)
  if input_message.lower() == 'hi':
    Text = "Hi "+user_data['first_name']+" "+user_data['last_name']
  
  messageData = {
      "text": Text
    }

  return messageData

def WikiMessage(message_text, user_data):
  Url = "https://www.googleapis.com/customsearch/v1?key=AIzaSyBEZBdHLIxayxR7DL9K0fY7lZAsPhYb3x8&cx=008848241005052050933:hqgz1t61kds&q="
  data = requests.get(Url+message_text).json()
  Title =  data["items"][0]["title"]
  Snippet = data["items"][0]["snippet"]
  wikiUrl = data["items"][0]["formattedUrl"]
  imgsource = ''
  if data["items"][0].get("pagemap"):
    if data["items"][0]["pagemap"].get("cse_image"):
      imgsource = data["items"][0]["pagemap"]["cse_image"][0]["src"]


  messageData = {
        "attachment": {
            "type": "template",
            "payload": {
                "template_type": "generic",
                "elements": [{
                    "title": Title,
                    "subtitle": Snippet,
                    "image_url": imgsource,
                    "buttons": [{
                        "type": "web_url",
                        "url": wikiUrl,
                        "title": Title
                    }],
                }]
            }
        }
    }

  # print messageData
  return messageData

def GenericMessage(message_text, user_data):
  Url = 'https://en.wikipedia.org/api/rest_v1/page/summary/'
  r = requests.get(Url+message_text)
  jsonContent = r.json()
  print jsonContent
  messageData = {
        "attachment": {
            "type": "template",
            "payload": {
                "template_type": "generic",
                "elements": [{
                    "title": "First card",
                    "subtitle": "Element #1 of an hscroll",
                    "image_url": "http://messengerdemo.parseapp.com/img/rift.png",
                    "buttons": [{
                        "type": "web_url",
                        "url": "https://www.messenger.com",
                        "title": "web url"
                    }, {
                        "type": "postback",
                        "title": "Buy",
                        "payload": "buy",
                    },{
                        "type": "postback",
                        "title": "Rent",
                        "payload": "rent",
                    }],
                }, {
                    "title": "Second card",
                    "subtitle": "Element #2 of an hscroll",
                    "image_url": "http://messengerdemo.parseapp.com/img/gearvr.png",
                    "buttons": [{
                        "type": "postback",
                        "title": "Fourth",
                        "payload": "fourth",
                    }],
                }]
            }
        }
    }
  return messageData

def MagicGenQuick(myList, message_text, user_data):
  payloadList = []
  for item in myList:
    payloadList.append({
                        "content_type": "text",
                        "title": item[0],
                        "payload": item[1],
                    })
  messageData = {
    "text":message_text,
    "quick_replies": payloadList
  }
  return messageData

def MagicGenMessage(myList, message_text, user_data):
  payloadList = []
  for item in myList:
    payloadList.append({
                        "type": "postback",
                        "title": item[0],
                        "payload": item[1],
                    })
  
  messageData = {
        "attachment": {
            "type": "template",
            "payload": {
                "template_type": "generic",
                "elements": [{
                    "title": message_text,
                    "buttons": payloadList,
                }]
            }
        }
    }
  return messageData


def getFB(fbid):
  global PAGE_ACCESS_TOKEN
  # user_details_url = "https://graph.facebook.com/v2.6/%s"%fbid
  # user_details_params = {'fields': 'email, first_name, last_name, hometown, id', 'access_token': PAGE_ACCESS_TOKEN}
  # user_details = requests.get(user_details_url, params=user_details_params).json()
  #joke_text = 'Yo '+user_details['first_name']+'..!' + joke_text

  # return user_details
  resp =  requests.get("https://graph.facebook.com/v2.6/%s?access_token=EAANZAbOErD3cBAIPPCfcScZAIsXY8JsPILWKXqpAlJvzmGAZBkg2BqW1ZBWvLF0WQmx43ZAO7FjYsRx0iEorvlORU7KQS4k9lC5mFFkOZC81JI3wFz6k4SbILhW5ipi8VZCPiBhqK27Ah2aN89poPvKqjKkBSO4G7gc0Xzq5g2WvQZDZD"%fbid)
  return resp.json()


def returnMsg():
  return "Hello the world!"
