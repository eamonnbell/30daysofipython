import os
import shlex
import urllib
import wikipedia
import requests
import json

from flask import Flask
from flask_slack import Slack

app = Flask(__name__)
slack = Slack(app)

app.add_url_rule('/', view_func=slack.dispatch)

WEBHOOK_URL = ''

@slack.command('fido', token='', team_id='', methods=['POST'])
def test(**kwargs):
    text = kwargs.get('text')
    response = parse(text)

    hook_ok = respond(response_text=response)

    if not hook_ok:
        return slack.response("Problem with the WebHook.")
    else:
        return slack.response("woof (fido fetched your request OK)")

def parse(text):
    valid_commands = ['IMSLP', 'WIKI']
    tokens = shlex.split(text) 
    verb = tokens[0].upper()

    if verb not in valid_commands:
        return "Invalid command."

    arguments = tokens[1:]

    if verb == 'IMSLP':
        return imslp(" ".join(arguments))
    elif verb == 'WIKI':
        return wiki(" ".join(arguments))
    else:
        return "Invalid command."

def imslp(query):
    base = 'https://www.google.com/search?q=site:imslp.org+'
    suffix = urllib.quote_plus(query)
    return '<{}>'.format(base + suffix)

def wiki(query):
    suggestion = wikipedia.search(query)[0]
    url = wikipedia.page(suggestion).url
    return '<{}>'.format(url) + '\n' + wikipedia.summary(suggestion, sentences=2) + '...'

def respond(response_text, webhook_url=WEBHOOK_URL):
    response = {'text' : response_text, 'unfurl_links' : True}
    payload = json.dumps(response)
    r = requests.post(webhook_url, data=payload)
    return r.status_code == requests.codes.ok
