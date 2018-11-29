import json
from flask import Flask, jsonify, make_response, request
from github import Github

TOKEN = "e279918c621ed22ea8ec4243c1c7821074118b5a"

app = Flask(__name__)
log = app.logger


@app.route('/webhook', methods=['POST'])
def webhook():
    # Get request parameters
    req = request.get_json(force=True)
    intent = req.get('queryResult').get('intent').get('displayName')

    # Check if the request is for the translate action
    if 'pr.state' in intent:
        pr =  int(req['queryResult']['parameters'].get('number-integer'))
        output = git_details(pr)
        
        res = {'fulfillmentText': output}
    else:
        # If the request is not to the translate.text action throw an error
        log.error('Unexpected action requested: %s', json.dumps(req))
        res = {'fulfillmentText': 'Sorry, there was a system failure'}

    return make_response(jsonify(res))

def git_details(number):
    g = Github(TOKEN)
    repo = g.get_repo("zowe/api-layer")
    try:
        pull = repo.get_pull(number)
        message = f"Pull request {number} is {pull.state}."
        if(pull.state!='closed'):
            message=message+f"\n     Created by: {pull.user.login}"
            reviewers = ""
            for rev in pull.raw_data['requested_reviewers']:
                reviewers = reviewers + " " +rev['login']
            message=message+f"\n     Waiting for reviewers:{reviewers}"
        return message
    except:
        return f"There is no pull request with the number {number}."

def dump(obj):
   for attr in dir(obj):
       if hasattr( obj, attr ):
           print( "obj.%s = %s" % (attr, getattr(obj, attr)))

if __name__ == '__main__':
    app.run(debug=True)

# .\ngrok.exe http 5000