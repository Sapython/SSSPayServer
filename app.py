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
from core.paysprint.Recharge import Recharge
from core.paysprint.HLR import HLR
from core.paysprint.billPayment import BillPayment
from core.paysprint.LIC import LIC
from core.paysprint.FastTag import FastTag

cred = credentials.Certificate(
    "keys/ssspay-prod-firebase-adminsdk-ouiri-dffb470966.json")
firebase_admin.initialize_app(cred)
# pylint: disable=C0103
app = Flask(__name__)
CORS(app)
aeps = AEPS(app)
authService = Authentication(auth, app)
messaging = Messaging()
LpgInstance = LPG(app)
DthInstance = Recharge(app)
HlrInstance = HLR(app)
RechargeInstance = Recharge(app)
BillPaymentInstance = BillPayment(app)
LicInstance = LIC(app)
FastTagInstance = FastTag(app)

def authorize():
    if (request.is_json):
        try:
            return authService.verifyToken(request.json)
        except Exception as e:
            return {'error': 'Invalid token'}, 400
    else:
        return ({'error': 'No token'}, 400)


@app.route('/', methods=['GET', 'POST'])
def test():
    # authorize()
    auth = authorize()
    if(auth[1] != 200):
        return jsonify(auth[0]), auth[1]
    # get current IP
    service = os.environ.get('K_SERVICE', 'Unknown service')
    revision = os.environ.get('K_REVISION', 'Unknown revision')
    return jsonify({"ip": requests.get('http://checkip.dyndns.org/').text, "service": service, "revision": revision})


@app.route('/favicon.ico', methods=['GET'])
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/sendSingleSMS', methods=['POST'])
def sendSingleSMS():
    auth = authorize()
    if(auth[1] != 200):
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


@app.route('/sendMultipleSMS', methods=['POST'])
def sendMultipleSMS():
    auth = authorize()
    if(auth[1] != 200):
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


@app.route('/scheduleSMS', methods=['POST'])
def scheduleSMS():
    auth = authorize()
    if(auth[1] != 200):
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
            response = messaging.scheduleSMS(
                message, phoneNo, schedule, priority)
            return jsonify({'success': response.text}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    else:
        return jsonify({'error': "We didn't received your data in json format "}), 400


@app.route('/getSMSBalance', methods=['GET'])
def getSMSBalance():
    auth = authorize()
    if(auth[1] != 200):
        return jsonify(auth[0]), auth[1]
    try:
        response = messaging.getBalance()
        return jsonify({'success': response}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/getMobileOperatorDetail', methods=['GET'])
def getMobileOperatorDetail():
    auth = authorize()
    if(auth[1] != 200):
        return jsonify(auth[0]), auth[1]
    try:
        response = messaging.getMobileOperatorDetail()
        return jsonify({'success': response}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/getLpgOperators', methods=['POST'])
def getLpgOperatorList():
    auth = authorize()
    if(auth[1] != 200):
        return jsonify(auth[0]), auth[1]

    try:
        response = LpgInstance.getOperatorList(mode='online')
        return jsonify(response), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/fetchLpgDetails', methods=['POST'])
def fetchLpgDetails():
    auth = authorize()
    if(auth[1] != 200):
        return jsonify(auth[0]), auth[1]
    if (request.is_json):
        try:
            caNumber = request.json['customerNumber']
            operatorNo = request.json['operatorNumber']
        except Exception as e:
            return jsonify({'error': "Please provide a customerNumber and operatorNumber ", "mainError": str(e)}), 400
        try:
            response = LpgInstance.fetchLpgDetails(caNumber, operatorNo)
            return jsonify(response), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    else:
        return jsonify({'error': "We didn't received your data in json format "}), 400


@app.route('/lpgRecharge', methods=['POST'])
def rechargeLpg():
    auth = authorize()
    if(auth[1] != 200):
        return jsonify(auth[0]), auth[1]
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
            response = LpgInstance.rechargeLpg(
                caNumber, operatorNo, amount, ad1, ad2, ad3, referenceId, latitude, longitude)
            return jsonify(response), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    else:
        return {'error': "We didn't received your data in json format "}, 400


@app.route('/lpgStatusInquiry', methods=['POST'])
def LpgStatusInquiry():
    auth = authorize()
    if(auth[1] != 200):
        return jsonify(auth[0]), auth[1]
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


@app.route('/getCustomerInfo', methods=['POST'])
def getCustomerInfo():
    # auth = authorize()
    # if(auth[1]!=200):
    #     return jsonify(auth[0]), auth[1]
    if request.is_json:
        try:
            number = request.json['number']
            opType = request.json['type']
            response = HlrInstance.getOperator(number, opType)
            return jsonify(response), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    else:
        return jsonify({'error': "We didn't received your data in json format "}), 400


@app.route('/getDthInfo', methods=['POST'])
def getDthInfo():
    # auth = authorize()
    # if(auth[1]!=200):
    #     return jsonify(auth[0]), auth[1]
    if request.is_json:
        try:
            number = request.json['caNumber']
            opType = request.json['operator']
            response = HlrInstance.getDthInfo(number, opType)
            return jsonify(response), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    else:
        return jsonify({'error': "We didn't received your data in json format "}), 400


@app.route('/getMobilePlan', methods=['POST'])
def getMobilePlan():
    # auth = authorize()
    # if(auth[1]!=200):
    #     return jsonify(auth[0]), auth[1]
    if request.is_json:
        try:
            circle = request.json['circle']
            operator = request.json['operator']
            response = HlrInstance.getPlanInfo(circle, operator)
            return jsonify(response), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    else:
        return jsonify({'error': "We didn't received your data in json format "}), 400


@app.route('/getOperatorsList', methods=['POST'])
def getOperatorsList():
    # auth = authorize()
    # if(auth[1]!=200):
    #     return jsonify(auth[0]), auth[1]
    try:
        response = RechargeInstance.getOperatorList()
        return jsonify(response), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/doRecharge', methods=['POST'])
def getOperatorInfo():
    # auth = authorize()
    # if(auth[1]!=200):
    #     return jsonify(auth[0]), auth[1]
    if request.is_json:
        try:
            operator = request.json['operator']
            caNumber = request.json['canumber']
            amount = request.json['amount']
            referenceId = request.json['referenceid']
            response = RechargeInstance.doRecharge(
                operator, caNumber, amount, referenceId)
            return jsonify(response), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    else:
        return jsonify({'error': "We didn't received your data in json format "}), 400


@app.route('/statusEnquiry', methods=['POST'])
def statusEnquiry():
    # auth = authorize()
    # if(auth[1]!=200):
    #     return jsonify(auth[0]), auth[1]
    if request.is_json:
        try:
            referenceId = request.json['referenceid']
            response = RechargeInstance.getStatusEnquiry(referenceId)
            return jsonify(response), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    else:
        return jsonify({'error': "We didn't received your data in json format "}), 400


@app.route('/getBillOperators', methods=['POST'])
def getBillOperators():
    # auth = authorize()
    # if(auth[1]!=200):
    #     return jsonify(auth[0]), auth[1]
    if request.is_json:
        try:
            response = BillPaymentInstance.getOperatorList('online')
            return jsonify(response), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    else:
        return jsonify({'error': "We didn't received your data in json format "}), 400


@app.route('/fetchBill', methods=['POST'])
def fetchBill():
    # auth = authorize()
    # if(auth[1]!=200):
    #     return jsonify(auth[0]), auth[1]
    if request.is_json:
        try:
            operatorNo = request.json['operator']
            caNumber = request.json['canumber']
            mode = request.json['mode']
            response = BillPaymentInstance.fetchBillDetails(
                operatorNo, caNumber, mode)
            return jsonify(response), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    else:
        return jsonify({'error': "We didn't received your data in json format "}), 400


@app.route('/payBill', methods=['POST'])
def payBill():
    # auth = authorize()
    # if(auth[1]!=200):
    #     return jsonify(auth[0]), auth[1]
    if request.is_json:
        try:
            operatorNo = request.json['operator']
            caNumber = request.json['caNumber']
            amount = request.json['amount']
            referenceId = request.json['referenceId']
            latitude = request.json['latitude']
            longitude = request.json['longitude']
            mode = request.json['mode']
            billAmount = request.json['billAmount']
            billNetAmount = request.json['billNetAmount']
            billDate = request.json['billDate']
            dueDate = request.json['dueDate']
            acceptPayment = request.json['acceptPayment']
            acceptPartPay = request.json['acceptPartpay']
            cellNumber = request.json['cellNumber']
            userName = request.json['username']
            response = BillPaymentInstance.payBill(operatorNo, caNumber, amount, referenceId, latitude, longitude,
                                                   mode, billAmount, billNetAmount, billDate, dueDate, acceptPayment, acceptPartPay, cellNumber, userName)
            return jsonify(response), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    else:
        return jsonify({'error': "We didn't received your data in json format "}), 400


@app.route('/billStatusEnquiry')
def billStatusEnquiry():
    # auth = authorize()
    # if(auth[1]!=200):
    #     return jsonify(auth[0]), auth[1]
    if request.is_json:
        try:
            referenceId = request.json['referenceid']
            response = BillPaymentInstance.statusEnquiry(referenceId)
            return jsonify(response), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    else:
        return jsonify({'error': "We didn't received your data in json format "}), 400

@app.route('/fetchLicBill')
def fetchLicBill():
    # auth = authorize()
    # if(auth[1]!=200):
    #     return jsonify(auth[0]), auth[1]
    if request.is_json:
        try:
            caNumber = request.json['caNumber']
            email = request.json['email']
            mode = request.json['mode']
            response = LicInstance.fetchLicBill(caNumber, email, mode)
            return jsonify(response), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    else:
        return jsonify({'error': "We didn't received your data in json format "}), 400

@app.route('/payLicBill')
def payLicBill():
    # auth = authorize()
    # if(auth[1]!=200):
    #     return jsonify(auth[0]), auth[1]
    if request.is_json:
        try:
            caNumber = request.json['caNumber']
            amount = request.json['amount']
            email = request.json['email']
            latitude = request.json['latitude']
            longitude = request.json['longitude']
            mode = request.json['mode']
            policyNumber1 = request.json['policyNumber1']
            policyNumber2 = request.json['policyNumber2']
            referenceId = request.json['referenceId']
            billNo = request.json['billNo']
            billAmount = request.json['billAmount']
            billNetAmount = request.json['billNetAmount']
            billDate = request.json['billDate']
            dueFrom = request.json['dueFrom']
            dueTo = request.json['dueTo']
            validationId = request.json['validationId']
            billId = request.json['billId']
            acceptPayment = request.json['acceptPayment']
            acceptPartPay = request.json['acceptPartpay']
            cellNumber = request.json['cellNumber']
            userName = request.json['username']
            response = LicInstance.payLicBill(caNumber, mode, amount, email, policyNumber1, policyNumber2, referenceId, latitude, longitude,
                                                   billNo, billAmount, billNetAmount, billDate,acceptPayment, acceptPartPay, cellNumber, dueFrom, dueTo, validationId,billId)
            return jsonify(response), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    else:
        return jsonify({'error': "We didn't received your data in json format "}), 400

@app.route('/getLicStatus')
def LicStatus():
    # auth = authorize()
    # if(auth[1]!=200):
    #     return jsonify(auth[0]), auth[1]
    if request.is_json:
        try:
            referenceId = request.json['referenceid']
            response = LicInstance.getLicStatus(referenceId)
            return jsonify(response), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    else:
        return jsonify({'error': "We didn't received your data in json format "}), 400

@app.route('/getFastTagOperatorList')
def getFastTagOperatorList():
    # auth = authorize()
    # if(auth[1]!=200):
    #     return jsonify(auth[0]), auth[1]
    if request.is_json:
        try:
            response = FastTagInstance.getOperatorsList()
            return jsonify(response), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    else:
        return jsonify({'error': "We didn't received your data in json format "}), 400

@app.route('/fastTagDetails')
def fastTagDetails():
    # auth = authorize()
    # if(auth[1]!=200):
    #     return jsonify(auth[0]), auth[1]
    if request.is_json:
        try:
            operatorNo = request.json['operator']
            caNumber = request.json['caNumber']
            response = FastTagInstance.fetchConsumerDetails(operatorNo, caNumber)
            return jsonify(response), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    else:
        return jsonify({'error': "We didn't received your data in json format "}), 400

@app.route('/rechargeFastTag')
def rechargeFastTag():
    # auth = authorize()
    # if(auth[1]!=200):
    #     return jsonify(auth[0]), auth[1]
    if request.is_json:
        try:
            operatorNo = request.json['operator']
            caNumber = request.json['caNumber']
            amount = request.json['amount']
            latitude = request.json['latitude']
            longitude = request.json['longitude']
            mode = request.json['mode']
            referenceId = request.json['referenceId']
            cellNumber = request.json['cellNumber']
            userName = request.json['username']
            billAmount = request.json['billAmount']
            billNetAmount = request.json['billNetAmount']
            dueDate = request.json['dueDate']
            maxBillAmount = request.json['maxBillAmount']
            acceptPayment = request.json['acceptPayment']
            acceptPartPay = request.json['acceptPartPay']
            cellNumber = request.json['cellNumber']
            userName = request.json['username']
            response = FastTagInstance.recharge(operatorNo, caNumber, amount, referenceId, latitude, longitude, billAmount, billNetAmount, dueData, maxBillAmount, acceptPayment, acceptPartPay, cellNumber, userName)
            return jsonify(response), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 400

@app.route('/getFastTagStatus')
def getFastTagStatus():
    # auth = authorize()
    # if(auth[1]!=200):
    #     return jsonify(auth[0]), auth[1]
    if request.is_json:
        try:
            referenceId = request.json['referenceid']
            response = FastTagInstance.getFastTagStatus(referenceId)
            return jsonify(response), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    else:
        return jsonify({'error': "We didn't received your data in json format "}), 400

if __name__ == '__main__':
    # server_port = os.environ.get('PORT', '8081')
    app.run(debug=False, port=8081, host='0.0.0.0')
