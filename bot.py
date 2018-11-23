import json
from flask import Flask, jsonify, make_response, request
app = Flask(__name__)
log = app.logger


@app.route('/webhook', methods=['POST'])
def webhook():
    """This method handles the http requests for the Dialogflow webhook
    This is meant to be used in conjunction with the translate Dialogflow agent
    """

    # Get request parameters
    req = request.get_json(force=True)
    intent = req.get('queryResult').get('intent').get('displayName')

    log.error('Unexpected action requested: %s', json.dumps(req))


    # Check if the request is for the translate action
    if intent == 'pr.state':
        pr =  req['queryResult']['parameters'].get('number-integer')
        # log.info("State of PR %d has been requested" % pr)
        output = "PR %d is the perfect state!" % pr

        # Compose the response to Dialogflow
        res = {'fulfillmentText': output}
    else:
        # If the request is not to the translate.text action throw an error
        log.error('Unexpected action requested: %s', json.dumps(req))
        res = {'fulfillmentText': 'Sorry, there was a system failure'}

    return make_response(jsonify(res))

if __name__ == '__main__':
    app.run(debug=True)