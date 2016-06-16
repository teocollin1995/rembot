import json
import logging
import urllib
import urllib2
from flask import Flask, Response, request
from google.appengine.api import urlfetch, memcache
from google.appengine.ext import ndb
from dateutil import parser
import time
app = Flask(__name__)

#constant for connecting to telegram
TOKEN = "230588661:AAHxRwP4fH473Sva_XQqF8IAvJGfFtqRH_o"
BASE_URL = 'https://api.telegram.org/bot' + TOKEN + '/'


#ndd records 

class CronJob(ndb.Model):
    timefloat = ndb.FloatProperty()
    chat_id = ndb.StringProperty()
    message_id = ndb.StringProperty()
    msg = ndb.StringProperty()

def give_response(chat_id, message_id, msg):
    resp = urllib2.urlopen(BASE_URL + 'sendMessage', urllib.urlencode({
        'chat_id': str(chat_id),
        'text': msg,
        'disable_web_page_preview': 'true',
        'reply_to_message_id': str(message_id),
    })).read()
    return(resp)


#we are about to be liberal with timestamps but it is okay because all appengine machines are on UTC and I will make all users input as UTC... or else
#to be clear, we heavily rely on all apengine servers being UTC


    

@app.route('/cron')
def cron_min():
    current_time = time.time()
    lower_bound = current_time - 31 #large enough range to get what we want with a little error
    upper_bound = current_time + 31
    query = CronJob.query(CronJob.timefloat >= lower_bound, CronJob.timefloat <= upper_bound)
    logging.info(str(query))
    for x in query:
        logging.info(str(x))
        give_response(x.chat_id,x.message_id,x.msg)
    logging.info("Cron happened")
    response = Response("", status=200)
    return(response)


@app.route('/setwh')
def set_webhook():
    """Exists to setup the webhook from the telegram api to the appengine site"""
    urlfetch.set_default_fetch_deadline(60)
    return json.dumps(json.load(urllib2.urlopen(BASE_URL + 'setWebhook', urllib.urlencode({'url': "https://rembot-1343.appspot.com/webhook"}))))



@app.route('/webhook', methods=["PUT", "POST"])
def webhook():
    urlfetch.set_default_fetch_deadline(60)
    requestbody = request.get_json()
    logging.info("raw request:")
    logging.info(requestbody)
    message = requestbody['message']
    chat = message['chat']
    chat_id = str(chat['id'])
    message = requestbody['message']
    text = message.get('text')
    message_id = message.get('message_id')
    timefloat = None
    msg = None
    if text[0:5] == "/cron":
        try:
            date = text.split('[')[1].split(']')[0]
            timefloat = time.mktime((parser.parse(date)).timetuple()) #again, we are only ever in UTC time...
        except:
            give_response(chat_id,message_id,"INVALID TIME, Ass!")
            response = Response(requestbody, status=200)
            return(response)
        try:
            msg = text.split('[')[2].split(']')[0]
        except:
            give_response(chat_id,message_id,"INVALID MSG, Ass!")
            response = Response(requestbody, status=200)
            return(response)
        if timefloat == None or msg == None:
            give_response(chat_id,message_id,"INVALID TIME or nessage, Ass!")
            response = Response(requestbody, status=200)
            return(response)
        else:
            cron = CronJob(timefloat=timefloat,chat_id=str(chat_id),message_id=str(message_id),msg=str(msg))
            cron.put()
            give_response(chat_id,message_id,"Scheduled message for this chat at unix time: {0}".format(timefloat))

        response = Response(requestbody, status=200)
        return(response)
    else:
        response = Response(requestbody, status=200)
        return(response)

    give_response(chat_id,message_id,str(text))
    response = Response(requestbody, status=200)
    return(response)

    
@app.route('/')
def hello():
    """Return a friendly HTTP greeting."""
    return 'Hello World!'


@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.', 404


@app.errorhandler(500)
def application_error(e):
    """Return a custom 500 error."""
    return 'Sorry, unexpected error: {}'.format(e), 500
