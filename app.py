"""
A sample Hello World server.
"""
import os

import firebase_admin
import requests
from firebase_admin import auth, credentials
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS

from core.authentication.auth import Authentication
from core.paysprint.AEPS import AEPS

from core.messaging.messaging import Messaging
from core.paysprint.LPG import LPG
cred = credentials.Certificate("keys/ssspay-prod-firebase-adminsdk-ouiri-dffb470966.json")
firebase_admin.initialize_app(cred)
# pylint: disable=C0103
app = Flask(__name__) 
CORS(app)
aeps = AEPS(app)
authService = Authentication(auth,app)
messaging = Messaging()
LpgInstance = LPG(app)

def authorize():
    if (request.is_json):
        try:
            return authService.verifyToken(request.json())
        except Exception as e:
            print('TRT Exception: ', e)
    else:
        return ({'error': 'No token'}, 400)

@app.route('/favicon.ico',methods=['GET'])
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/getAepsBalance',methods=['POST'])
def getAepsBalance():
    auth = authorize()
    if(auth[1]!=200):
        return jsonify(auth[0]), auth[1]
    aeps.getBalance(0.543534, 0.54353453, '234567890', '87687687', '192.168.29.208', '12341234234', 'bank',
                    '23d4f5678g9h', 'tetetet', 'data', 'pipe', '12 65 76 56', 'transactionType', 'subMerchantId', 'Yes')
    return 'Encrypted'


@app.route('/sendSingleSMS',methods=['POST'])
def sendSingleSMS():
    auth = authorize()
    if(auth[1]!=200):
        return jsonify(auth[0]), auth[1]
    try:
        phoneNo = request.json['phoneNo']
        message = request.json['message']
        priority = request.json['priority']
    except Exception as e:
        return {'error': 'SMS request should contain phone number without (+91), message (<260 Chars) and priority (dnd/ndnd)' + e}, 400
    try:
        response = messaging.sendSingleSMS(message, phoneNo, priority)
        print(response.text)
        return {'success': response.text}, 200
    except Exception as e:
        return {'error': str(e)}, 400

@app.route('/sendMultipleSMS',methods=['POST'])
def sendMultipleSMS():
    auth = authorize()
    if(auth[1]!=200):
        return jsonify(auth[0]), auth[1]
    try:
        phoneNo = request.json['phoneNo']
        message = request.json['message']
        priority = request.json['priority']
    except Exception as e:
        return {'error': 'SMS request should contain phone number without (+91), message (<260 Chars) and priority (dnd/ndnd)' + e}, 400
    try:
        response = messaging.sendMultiSMS(message, phoneNo, priority)
        return {'success': response.text}, 200
    except Exception as e:
        return {'error': str(e)}, 400

@app.route('/scheduleSMS',methods=['POST'])
def scheduleSMS():
    auth = authorize()
    if(auth[1]!=200):
        return jsonify(auth[0]), auth[1]
    try:
        phoneNo = request.json['phoneNo']
        message = request.json['message']
        priority = request.json['priority']
        schedule = request.json['schedule']
    except Exception as e:
        return {'error': 'SMS request should contain phone number without (+91), message (<260 Chars) and priority (dnd/ndnd)' + e}, 400
    try:
        response = messaging.scheduleSMS(message, phoneNo, schedule, priority)
        return {'success': response.text}, 200
    except Exception as e:
        return {'error': str(e)}, 400

@app.route('/getSMSBalance')
def getSMSBalance():
    auth = authorize()
    if(auth[1]!=200):
        return jsonify(auth[0]), auth[1]
    try:
        response = messaging.getBalance()
        return {'success': response}, 200
    except Exception as e:
        return {'error': str(e)}, 400

@app.route('/getMobileOperatorDetail')
def getMobileOperatorDetail():
    auth = authorize()
    if(auth[1]!=200):
        return jsonify(auth[0]), auth[1]
    try:
        response = messaging.getMobileOperatorDetail()
        return {'success': response}, 200
    except Exception as e:
        return {'error': str(e)}, 400

@app.route('/getLpgOperators',methods=['POST'])
def getLpgOperatorList():
    # auth = authorize()
    # if(auth[1]!=200):
    #     return jsonify(auth[0]), auth[1]
    try:
        response = LpgInstance.getOperatorList(mode='online')
        return jsonify(response), 200
    except Exception as e:
        return {'error': str(e)}, 400

@app.route('/',methods=['GET'])
def test():
    # authorize()
    auth = authorize()
    if(auth[1]!=200):
        return jsonify(auth[0]), auth[1]
    # get current IP
    service = os.environ.get('K_SERVICE', 'Unknown service')
    revision = os.environ.get('K_REVISION', 'Unknown revision')
    return jsonify({"ip":requests.get('http://checkip.dyndns.org/').text, "service":service, "revision":revision})

if __name__ == '__main__':
    # server_port = os.environ.get('PORT', '8081')
    app.run(debug=False, port=8081, host='0.0.0.0')
