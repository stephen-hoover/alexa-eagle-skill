import logging
import sys

from requests import ReadTimeout

import config
import handle
import reply

log = logging.getLogger(__name__)

# --------------------------- Lambda Function ----------------------------------
def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    logging.basicConfig(level=getattr(config, 'log_level', 'INFO'),
                        stream=sys.stderr)

    # This `if` prevents other Skills from using this Lambda
    if event['session']['application']['applicationId'] != config.APP_ID:
        raise ValueError("Invalid Application ID")

    try:
        if event['request']['type'] == "IntentRequest":
            return handle.intent(event['request'], event['session'])
        elif event['request']['type'] == "LaunchRequest":
            return reply.build("",  # TODO: Write this
                               is_end=False)
        elif event['request']['type'] == "SessionEndedRequest":
            return reply.build("Goodbye!", is_end=True)
        else:
            # I don't think there's any other kinds of requests.
            return reply.build("",  # TODO: Write this
                               is_end=False)
    except ReadTimeout:
        log.exception('Timeout accessing Rainforest cloud.')
        return reply.build("I couldn't access the Rainforest Cloud.",
                           is_end=True)
    except Exception as err:  # NOQA
        log.exception('Unhandled exception for event\n%s\n' % str(event))
        return reply.build("Sorry, something went wrong.",
                           persist=event['session'].get('attributes', {}),
                           is_end=True)
