import json
import logging
import urllib
import urllib2
from flask import Flask, Response, request
from google.appengine.api import urlfetch, memcache
from google.appengine.ext import ndb
app = Flask(__name__)

#constant for connecting to telegram
TOKEN = "230588661:AAHxRwP4fH473Sva_XQqF8IAvJGfFtqRH_o"
BASE_URL = 'https://api.telegram.org/bot' + TOKEN + '/'


#ndd records 

class CronJob(ndb.Model):
    time = ndb.DateTimeProperty()
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
