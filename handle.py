"""Handle requests sent by Echo

https://developer.amazon.com/public/solutions/alexa/alexa-skills-kit/docs/alexa-skills-kit-interface-reference
The requests are JSON formatted as:
{
  "version": "string",
  "session": {
    "new": boolean,
    "sessionId": "string",
    "application": {
      "applicationId": "string"
    },
    "attributes": {
      "string": object
    },
    "user": {
      "userId": "string",
      "accessToken": "string"
    }
  },
  "request": object
}

There are three kinds of requests: IntentRequest, LaunchRequest, and SessionEndedRequest

IntentRequest:
{
  "type": "IntentRequest",
  "requestId": "string",
  "timestamp": "string",
  "intent": {
    "name": "string",
    "slots": {
      "string": {
        "name": "string",
        "value": "string"
      }
    }
  }
}
"""
from __future__ import print_function, division
import logging
import os
import reply
import time

from eagle_http.eagle_http import eagle_http

import config

log = logging.getLogger(__name__)


def _time_string():
    """Return a string representing local time"""
    os.environ['TZ'] = config.time_zone
    time.tzset()
    return time.asctime()


def _poller():
    return eagle_http(config.username, config.password, config.cloud_id,
                      noisy=False, json=True, keep_history=False)


def intent(req, session):
    """Identify and handle IntentRequest objects

    Parameters
    ----------
    req : dict
        JSON following the Alexa "IntentRequest" schema
    session : dict
        JSON following the Alexa "Session" schema

    Returns
    -------
    dict
        JSON following the Alexa reply schema
    """
    intent = req['intent']
    if session.setdefault('attributes', {}) is None:
        # Ensure that there's always a dictionary under "attributes".
        session['attributes'] = {}

    # Dispatch each Intent to the correct handler.
    if intent['name'] == 'CheckDemandIntent':
        return check_demand(intent, session)
    elif intent['name'] == 'CheckPriceIntent':
        return check_price(intent, session)
    elif intent['name'] == 'CheckSummationIntent':
        return check_consumption(intent, session)
    elif intent['name'] in ['AMAZON.StopIntent', 'AMAZON.CancelIntent']:
        return reply.build("Okay, exiting.", is_end=True)
    elif intent['name'] == 'AMAZON.HelpIntent':
        return reply.build("This sentence is helpful.",  # TODO
                           is_end=False)
    else:
        return reply.build("I didn't understand that. Try again?",
                           persist=session['attributes'],
                           is_end=False)


def check_demand(intent, session):
    demand = _poller().get_instantaneous_demand()['Demand']

    utterance = "Current demand is "
    if demand < 1:
        utterance += "%d Watts." % (demand * 1000)
    else:
        utterance += "%d kilowatts." % demand
    return reply.build(utterance, is_end=True)


def check_price(intent, session):
    price = _poller().get_price()['Price']
    card_text = "$%.2f per kilowatt-hour" % (price/100)
    return reply.build("It's %s %s." % (str(price)[:-2], str(price)[-2:]),
                       card_title="Your Electicity Price",
                       card_text='\n'.join(card_text),
                       is_end=True)


def check_consumption(intent, session):
    return reply.build("This code not yet written.", is_end=True)
