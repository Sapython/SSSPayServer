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
            return authService.verifyToken(request.json)
        except Exception as e:
            return {'error': 'Invalid token'}, 400
    else:
        return ({'error': 'No token'}, 400)

@app.route('/favicon.ico',methods=['GET'])
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/sendSingleSMS',methods=['POST'])
def sendSingleSMS():
    auth = authorize()
    if(auth[1]!=200):
        return jsonify(auth[0]), auth[1]
    if (request.is_json):
        try:
            phoneNo = request.json['phoneNo']
            message = request.json['message']
            priority = request.json['priority']
        except Exception as e:
            return jsonify({'error': 'SMS request should contain phone number without (+91), message (<260 Chars) and priority (dnd/ndnd)' + e}), 400
        try:
            response = messaging.sendSingleSMS(message, phoneNo, priority)
            print(response.text)
            return jsonify({'success': response.text}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    else:
        return jsonify({'error': "We didn't received your data in json format "}), 400

@app.route('/sendMultipleSMS',methods=['POST'])
def sendMultipleSMS():
    auth = authorize()
    if(auth[1]!=200):
        return jsonify(auth[0]), auth[1]
    if (request.is_json):
        try:
            phoneNo = request.json['phoneNo']
            message = request.json['message']
            priority = request.json['priority']
        except Exception as e:
            return jsonify({'error': 'SMS request should contain phone number without (+91), message (<260 Chars) and priority (dnd/ndnd)' + e}), 400
        try:
            response = messaging.sendMultiSMS(message, phoneNo, priority)
            return jsonify({'success': response.text}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    else:
        return jsonify({'error': "We didn't received your data in json format "}), 400

@app.route('/scheduleSMS',methods=['POST'])
def scheduleSMS():
    auth = authorize()
    if(auth[1]!=200):
        return jsonify(auth[0]), auth[1]
    if (request.is_json):
        try:
            phoneNo = request.json['phoneNo']
            message = request.json['message']
            priority = request.json['priority']
            schedule = request.json['schedule']
        except Exception as e:
            return jsonify({'error': 'SMS request should contain phone number without (+91), message (<260 Chars) and priority (dnd/ndnd)' + e}), 400
        try:
            response = messaging.scheduleSMS(message, phoneNo, schedule, priority)
            return jsonify({'success': response.text}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    else:
        return jsonify({'error': "We didn't received your data in json format "}), 400

@app.route('/getSMSBalance',methods=['GET'])
def getSMSBalance():
    auth = authorize()
    if(auth[1]!=200):
        return jsonify(auth[0]), auth[1]
    try:
        response = messaging.getBalance()
        return jsonify({'success': response}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/getMobileOperatorDetail',methods=['GET'])
def getMobileOperatorDetail():
    auth = authorize()
    if(auth[1]!=200):
        return jsonify(auth[0]), auth[1]
    try:
        response = messaging.getMobileOperatorDetail()
        return jsonify({'success': response}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/getLpgOperators',methods=['POST'])
def getLpgOperatorList():
    # auth = authorize()
    # if(auth[1]!=200):
    #     return jsonify(auth[0]), auth[1]
    
    try:
        response = LpgInstance.getOperatorList(mode='online')
        return jsonify(response), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/fetchLpgDetails',methods=['POST'])
def fetchLpgDetails():
    # auth = authorize()
    # if(auth[1]!=200):
    #     return jsonify(auth[0]), auth[1]
    if (request.is_json):
        try:
            caNumber = request.json['customerNumber']
            operatorNo = request.json['operatorNumber']
        except Exception as e:
            return jsonify({'error': "Please provide a customerNumber and operatorNumber ","mainError":str(e)}), 400
        try:
            response = LpgInstance.fetchLpgDetails(caNumber, operatorNo)
            return jsonify(response), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    else:
        return jsonify({'error': "We didn't received your data in json format "}), 400

@app.route('/lpgRecharge',methods=['POST'])
def rechargeLpg():
    # auth = authorize()
    # if(auth[1]!=200):
    #     return jsonify(auth[0]), auth[1]
    if (request.is_json):
        try:
            caNumber = request.json['customerNumber']
            operatorNo = request.json['operatorNumber']
            amount = request.json['amount']
            ad1 = request.json['ad1']
            ad2 = request.json['ad2']
            ad3 = request.json['ad3']
            referenceId = request.json['referenceId']
            latitude = request.json['latitude']
            longitude = request.json['longitude']
        except:
            return {'error': "Please provide a customerNumber, operatorNumber, amount, ad1, ad2, ad3, referenceId, latitude and longitude "}, 400
        try:
            response = LpgInstance.rechargeLpg(caNumber, operatorNo, amount, ad1, ad2, ad3, referenceId, latitude, longitude)
            return jsonify(response), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    else:
        return {'error': "We didn't received your data in json format "}, 400

@app.route('/lpgStatusInquiry',methods=['POST'])
def LpgStatusInquiry():
    # auth = authorize()
    # if(auth[1]!=200):
    #     return jsonify(auth[0]), auth[1]
    if (request.is_json):
        try:
            referenceId = request.json['referenceId']
        except:
            return jsonify({'error': "Please provide a referenceId "}), 400
        try:
            response = LpgInstance.getLpgRechargeStatus(referenceId)
            return jsonify(response), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    else:
        return jsonify({'error': "We didn't received your data in json format "}), 400
            

@app.route('/',methods=['GET','POST'])
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
