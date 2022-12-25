"""
SSSPay payment server
"""

version = "1.0.0"
import datetime
import logging
import os
import random
import time

import firebase_admin
## import google.cloud.logging
import requests
from firebase_admin import auth, credentials
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from core.authentication.auth import Authentication
from core.authentication.paysprintAuth import PaySprintAuth
from core.authentication.userManagement import UserManagement
from core.helpers.Qr import QR
from core.helpers.Transaction import Transaction
from core.helpers.CommisionAndCharges import CommissionAndCharges
from core.messaging.messaging import Messaging
from core.payment.payout.payout import Payout
from core.payment.wallet.wallet import Wallet
from core.paysprint.AEPS import AEPS
from core.paysprint.billPayment import BillPayment
from core.paysprint.FastTag import FastTag
from core.paysprint.HLR import HLR
from core.paysprint.LIC import LIC
from core.paysprint.LPG import LPG
from core.paysprint.Onboarding import Onboarding
from core.paysprint.Recharge import Recharge
from core.paysprint.Upi import UPI
import razorpay
from firebase_admin import firestore
from google.cloud.firestore_v1 import Increment
import builtins
import traceback
def print(*objs, **kwargs):
    my_prefix = "VER: "+version
    builtins.print(my_prefix, *objs, **kwargs)

# client = razorpay.Client(auth=("rzp_test_iXjGFXuZaNQ1Uk", "7od0YTzDp656LZT1qcNop4Nc"))
client = razorpay.Client(auth=("rzp_live_tlXdDUmbEQxwf9", "0bbPbrfVDHYc7gJNgCCbBxdr"))
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="keys/ssspay-prod-firebase-adminsdk-ouiri-dffb470966.json"

cred = credentials.Certificate(
    "keys/ssspay-prod-firebase-adminsdk-ouiri-dffb470966.json")
DEVELOPMENT = True
firebase_admin.initialize_app(cred)
fs = firestore.client()
## client = google.cloud.logging.Client()
## client.setup_logging()

# pylint: disable=C0103
app = Flask(__name__)
CORS(app)
aeps = AEPS(app,DEVELOPMENT)
authService = Authentication(auth, app)
messaging = Messaging()
LpgInstance = LPG(app, DEVELOPMENT)
DthInstance = Recharge(app)
HlrInstance = HLR(app, DEVELOPMENT)
RechargeInstance = Recharge(app)
BillPaymentInstance = BillPayment(app)
LicInstance = LIC(app)
FastTagInstance = FastTag(app)
userManagement = UserManagement(auth, app)
wallet = Wallet(app)
payout = Payout(app)
transactionInstance = Transaction(app, DEVELOPMENT)
qr = QR(DEVELOPMENT)
onboarding = Onboarding(app,logging)
upi = UPI(app)
HLR_WORKING = False
paysprintAuth = PaySprintAuth(app)
commissionManager = CommissionAndCharges()

def authorize():
    if DEVELOPMENT:
        return DEVELOPMENT, 200
    if (request.is_json):
        try:
            return authService.verifyToken(request.json)
        except Exception as e:
            ## logging.warning(e)
            return {'error': 'Invalid token'}, 400
    else:
        ## logging.warning('No token')
        return {'error': 'No token'}, 400


@app.route('/', methods=['GET', 'POST'])
def test():
    # authorize()
    auth = authorize()
    if(auth[1] != 200):
        return jsonify(auth[0]), auth[1]
    # get current IP
    service = os.environ.get('K_SERVICE', 'Unknown service')
    revision = os.environ.get('K_REVISION', 'Unknown revision')
    res= requests.get('http://checkip.dyndns.org/').text
    status = requests.get('https://api.paysprint.in/api/v1/service/balance/balance/authenticationcheck',headers = paysprintAuth.generatePaysprintAuthHeaders()).text
    return jsonify({"ip": res, "service": service, "revision": revision, "version": 2, "development": DEVELOPMENT,"status":status})


@app.route('/favicon.ico', methods=['POST'])
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

# Wallet Services


@app.route('/wallet/getBalance', methods=['POST'])
def getBalance():
    auth = authorize()
    if(auth[1] != 200):
        return jsonify(auth[0]), auth[1]
    if (request.is_json):
        if (request.json['uid'] is None):
            return {'error': 'uid is required'}, 400
        try:
            print(request.json['uid'])
            balance = wallet.get_balance(request.json['uid'])
            if (balance > 0):
                return {"balance": balance}
            else:
                return {"error": "No balance"}
        except Exception as e:
            if DEVELOPMENT:
                return {'error': str(e)}, 400
            return {'error': 'Invalid token'}, 400
    else:
        return {'error': "We didn't received your data in json format"}, 400


@app.route('/wallet/addBalance', methods=['POST'])
def addWalletBalance():
    auth = authorize()
    if(auth[1] != 200):
        return jsonify(auth[0]), auth[1]
    if (request.is_json):
        if (request.json['uid'] is None):
            return {'error': 'uid is required'}, 400
        if (request.json['amount'] is None):
            return {'error': 'amount is required'}, 400
        try:
            print(request.json['uid'])
            wallet.add_balance(request.json['uid'], request.json['amount'])
            return {"success": "Balance added successfully"}
        except Exception as e:
            ## logging.error(e)
            if DEVELOPMENT:
                return {'error': str(e)}, 400
            return {'error': 'Invalid token'}, 400
    else:
        return {'error': "We didn't received your data in json format"}, 400


@app.route('/wallet/deductBalance', methods=['POST'])
def deductWalletBalance():
    auth = authorize()
    if(auth[1] != 200):
        return jsonify(auth[0]), auth[1]
    if (request.is_json):
        if (request.json['uid'] is None):
            return {'error': 'uid is required'}, 400
        if (request.json['amount'] is None):
            return {'error': 'amount is required'}, 400
        try:
            print(request.json['uid'])
            wallet.deduct_balance(request.json['uid'], request.json['amount'])
            return {"success": "Balance deducted successfully"}
        except Exception as e:
            ## logging.error(e)
            if DEVELOPMENT:
                return {'error': str(e)}, 400
            return {'error': 'Invalid token'}, 400
    else:
        return {'error': "We didn't received your data in json format"}, 400

# Payout services


@app.route('/payout/createAccount', methods=['POST'])
def createPayOutContact():
    auth = authorize()
    if(auth[1] != 200):
        return jsonify(auth[0]), auth[1]
    if (request.is_json):
        if (request.json['uid'] is None):
            return {'error': 'uid is required'}, 400
        if (request.json['name'] is None):
            return {'error': 'name is required'}, 400
        if (request.json['email'] is None):
            return {'error': 'email is required'}, 400
        if (request.json['contact'] is None):
            return {'error': 'contact is required'}, 400
        try:
            print(request.json['uid'])
            payout.createAccount(request.json)
            return {"success": "Account created successfully"}
        except Exception as e:
            ## logging.error(e)
            if DEVELOPMENT:
                return {'error': str(e)}, 400
            return {'error': 'Invalid token'}, 400
    else:
        return {'error': "We didn't received your data in json format"}, 400


@app.route('/payout/allAccounts', methods=['POST'])
def getAllPayoutContacts():
    auth = authorize()
    if(auth[1] != 200):
        return jsonify(auth[0]), auth[1]
    if (request.is_json):
        try:
            accounts = payout.getAllAccounts()
            return {"accounts": accounts}
        except Exception as e:
            ## logging.error(e)
            if DEVELOPMENT:
                return {'error': str(e)}, 400
            return {'error': 'Invalid token'}, 400
    else:
        return {'error': "We didn't received your data in json format"}, 400


@app.route('/payout/getAccount', methods=['POST'])
def getPayoutContact():
    auth = authorize()
    if(auth[1] != 200):
        return jsonify(auth[0]), auth[1]
    if (request.is_json):
        if (request.json['accountId'] is None):
            return {'error': 'accountId is required'}, 400
        try:
            account = payout.getAccount(request.json['accountId'])
            return {"account": account}
        except Exception as e:
            ## logging.error(e)
            if DEVELOPMENT:
                return {'error': str(e)}, 400
            return {'error': 'Invalid token'}, 400
    else:
        return {'error': "We didn't received your data in json format"}, 400


@app.route('/payout/updateAccount', methods=['POST'])
def updatePayoutContact():
    auth = authorize()
    if(auth[1] != 200):
        return jsonify(auth[0]), auth[1]
    if (request.is_json):
        if (request.json['accountId'] is None):
            return {'error': 'accountId is required'}, 400
        if (request.json['name'] is None):
            return {'error': 'name is required'}, 400
        if (request.json['email'] is None):
            return {'error': 'email is required'}, 400
        if (request.json['contact'] is None):
            return {'error': 'contact is required'}, 400
        if (request.json['uid'] is None):
            return {'error': 'uid is required'}, 400
        try:
            print(request.json)
            payout.updateAccount(request.json)
            return {"success": "Account updated successfully"}
        except Exception as e:
            ## logging.error(e)
            if DEVELOPMENT:
                return {'error': str(e)}, 400
            return {'error': 'Invalid token'}, 400
    else:
        return {'error': "We didn't received your data in json format"}, 400


@app.route('/payout/activateAccount', methods=['POST'])
def activatePayoutContact():
    auth = authorize()
    if(auth[1] != 200):
        return jsonify(auth[0]), auth[1]
    if (request.is_json):
        if (request.json['accountId'] is None):
            return {'error': 'accountId is required'}, 400
        try:
            payout.activateAccount(request.json['accountId'])
            return {"success": "Account activated successfully"}
        except Exception as e:
            ## logging.error(e)
            if DEVELOPMENT:
                return {'error': str(e)}, 400
            return {'error': 'Invalid token'}, 400
    else:
        return {'error': "We didn't received your data in json format"}, 400


@app.route('/payout/deactivateAccount', methods=['POST'])
def deactivatePayoutContact():
    auth = authorize()
    if(auth[1] != 200):
        return jsonify(auth[0]), auth[1]
    if (request.is_json):
        if (request.json['accountId'] is None):
            return {'error': 'accountId is required'}, 400
        try:
            payout.deactivateAccount(request.json['accountId'])
            return {"success": "Account deactivated successfully"}
        except Exception as e:
            ## logging.error(e)
            if DEVELOPMENT:
                return {'error': str(e)}, 400
            return {'error': 'Invalid token'}, 400
    else:
        return {'error': "We didn't received your data in json format"}, 400


@app.route('/payout/connectFundAccount', methods=['POST'])
def connectFundAccount():
    auth = authorize()
    if(auth[1] != 200):
        return jsonify(auth[0]), auth[1]
    if (request.is_json):
        if (request.json['accountId'] is None):
            return {'error': 'accountId is required'}, 400
        if (request.json['account_type'] is None):
            return {'error': 'account_type is required'}, 400
        if (request.json['account_type'] == "bank_account"):
            if (request.json['bankAccountName'] is None):
                return {'error': 'bankAccountName is required'}, 400
            if (request.json['accountNumber'] is None):
                return {'error': 'accountNumber is required'}, 400
            if (request.json['ifsc'] is None):
                return {'error': 'ifsc is required'}, 400
        elif (request.json['account_type'] == "vpa"):
            if (request.json['vpa'] is None):
                return {'error': 'vpa is required'}, 400
        elif (request.json['account_type'] == "card"):
            if (request.json['cardNumber'] is None):
                return {'error': 'cardNumber is required'}, 400
            if (request.json['cardName'] is None):
                return {'error': 'cardName is required'}, 400
        else:
            return {'error': "account_type is invalid"}, 400
        try:
            payout.connectFundAccount(request.json)
            return {"success": "Account connected successfully"}
        except Exception as e:
            ## logging.error(e)
            if DEVELOPMENT:
                return {'error': str(e)}, 400
            return {'error': 'Invalid token'}, 400
    else:
        return {'error': "We didn't received your data in json format"}, 400


@app.route('/payout/getAllFundAccounts', methods=['POST'])
def getAllFundAccounts():
    auth = authorize()
    if(auth[1] != 200):
        return jsonify(auth[0]), auth[1]
    if (request.is_json):
        try:
            accounts = payout.getAllFundAccounts()
            return {"accounts": accounts}
        except Exception as e:
            ## logging.error(e)
            if DEVELOPMENT:
                return {'error': str(e)}, 400
            return {'error': 'Invalid token'}, 400
    else:
        return {'error': "We didn't received your data in json format"}, 400


@app.route('/payout/getFundAccountById', methods=['POST'])
def getFundAccountById():
    auth = authorize()
    if(auth[1] != 200):
        return jsonify(auth[0]), auth[1]
    if (request.is_json):
        if (request.json['accountId'] is None):
            return {'error': 'accountId is required'}, 400
        try:
            account = payout.getFundAccountById(request.json['accountId'])
            return {"account": account}
        except Exception as e:
            ## logging.error(e)
            if DEVELOPMENT:
                return {'error': str(e)}, 400
            return {'error': 'Invalid token'}, 400
    else:
        return {'error': "We didn't received your data in json format"}, 400


@app.route('/payout/createPayout', methods=['POST'])
def createPayout():
    auth = authorize()
    if(auth[1] != 200):
        return jsonify(auth[0]), auth[1]
    if (request.is_json):
        if (request.json['account_number'] is None):
            return {'error': 'account_number is required'}, 400
        if (request.json['fund_account_id'] is None):
            return {'error': 'fund_account_id is required'}, 400
        if (request.json['amount'] is None):
            return {'error': 'amount is required'}, 400
        if (request.json['mode'] is None):
            return {'error': 'mode is required'}, 400
        if (request.json['referenceId'] is None):
            return {'error': 'referenceId is required'}, 400
        if (request.json['narration'] is None):
            return {'error': 'narration is required'}, 400
        if (request.json['uid'] is None):
            return {'error': 'uid is required'}, 400
        try:
            payout.createPayout(request.json)
            return {"success": "Payout created successfully"}
        except Exception as e:
            ## logging.error(e)
            if DEVELOPMENT:
                return {'error': str(e)}, 400
            return {'error': 'Invalid token'}, 400
    else:
        return {'error': "We didn't received your data in json format"}, 400


@app.route('/payout/getAllPayouts', methods=['POST'])
def getAllPayouts():
    auth = authorize()
    if(auth[1] != 200):
        return jsonify(auth[0]), auth[1]
    if (request.is_json):
        try:
            if (request.json['account_number'] is None):
                return {'error': 'account_number is required'}, 400
            payouts = payout.getAllPayouts(request.json['account_number'])
            return {"payouts": payouts}
        except Exception as e:
            ## logging.error(e)
            if DEVELOPMENT:
                return {'error': str(e)}, 400
            return {'error': 'Invalid token'}, 400
    else:
        return {'error': "We didn't received your data in json format"}, 400


@app.route('/payout/getPayoutById', methods=['POST'])
def getPayoutById():
    auth = authorize()
    if(auth[1] != 200):
        return jsonify(auth[0]), auth[1]
    if (request.is_json):
        if (request.json['payout_id'] is None):
            return {'error': 'payout_id is required'}, 400
        try:
            payout = payout.getPayoutById(request.json['payout_id'])
            return {"payout": payout}
        except Exception as e:
            ## logging.error(e)
            if DEVELOPMENT:
                return {'error': str(e)}, 400
            return {'error': 'Invalid token'}, 400
    else:
        return {'error': "We didn't received your data in json format"}, 400


@app.route('/payout/cancelQueuedPayout', methods=['POST'])
def cancelQueuedPayout():
    auth = authorize()
    if(auth[1] != 200):
        return jsonify(auth[0]), auth[1]
    if (request.is_json):
        if (request.json['payout_id'] is None):
            return {'error': 'payout_id is required'}, 400
        try:
            payout.cancelQueuedPayout(request.json['payout_id'])
            return {"success": "Payout cancelled successfully"}
        except Exception as e:
            ## logging.error(e)
            if DEVELOPMENT:
                return {'error': str(e)}, 400
            return {'error': 'Invalid token'}, 400
    else:
        return {'error': "We didn't received your data in json format"}, 400


@app.route('/payout/expressPayout', methods=['POST'])
def expressPayout():
    auth = authorize()
    if(auth[1] != 200):
        return jsonify(auth[0]), auth[1]
    transactionValue = transactionInstance.getTransaction(
        request.json['uid'], request.json['transactionId'])
    if (transactionValue == None):
        return {'error': 'Transaction not found'}, 400
    if (not transactionInstance.checkBalance(transactionValue['amount'], request.json['uid'])):
        return {'error': 'Insufficient balance'}, 400

    if (request.is_json):
        if (transactionValue['extraData']['accountType'] is None):
            return {'error': 'accountType is required'}, 400
        if (transactionValue['extraData']['accountType'] == 'bank_account'):
            if (transactionValue['extraData']['account']['bankAccountName'] is None):
                return {'error': 'bankAccountName is required'}, 400
            if (transactionValue['extraData']['account']['ifsc'] is None):
                return {'error': 'ifsc is required'}, 400
            if (transactionValue['extraData']['account']['accountNumber'] is None):
                return {'error': 'accountNumber is required'}, 400
        elif (transactionValue['extraData']['accountType'] == 'vpa'):
            if (transactionValue['extraData']['account']['vpa'] is None):
                return {'error': 'vpa is required'}, 400
        elif (transactionValue['extraData']['accountType'] == 'card'):
            if (transactionValue['extraData']['account']['cardNumber'] is None):
                return {'error': 'cardNumber is required'}, 400
            if (transactionValue['extraData']['account']['cardName'] is None):
                return {'error': 'cardName is required'}, 400
        else:
            return {'error': 'Invalid accountType'}, 400
        if (transactionValue['extraData']['account']['name'] is None):
            return {'error': 'name is required'}, 400

        if (transactionValue['extraData']['account']['email'] is None):
            return {'error': 'email is required'}, 400

        if (transactionValue['extraData']['account']['contact'] is None):
            return {'error': 'contact is required'}, 400

        if (request.json['uid'] is None):
            return {'error': 'uid is required'}, 400

        if (transactionValue['extraData']['customerId'] is None):
            return {'error': 'customerId is required'}, 400

        if (transactionValue['idempotencyKey'] is None):
            return {'error': 'idempotencyKey is required'}, 400
        transactionValue['referenceId'] = request.json['transactionId']
        transactionValue['uid'] = request.json['uid']
        try:
            responseData = payout.quickPayout(
                transactionValue, transactionValue['extraData']['accountType'], transactionValue['idempotencyKey'])
            # print("ACTUAL RESPONSE", responseData)
            if (responseData[0]['status'] == 'queued' or responseData[0]['status'] == 'pending' or responseData[0]['status'] == 'processing'):
                message = 'Express Payout of amount '+str(transactionValue['amount'])+' for ' + str(
                    transactionValue['extraData']['customerId']) + ' is pending. Transaction id of this transaction is '+str(request.json['transactionId'])
                transactionInstance.pendingTransaction(
                    request.json['uid'], request.json['transactionId'], message, 'expressPayout', responseData[0])
                return {"queued": "Payout created successfully","data":responseData}, 200
            elif (responseData[0]['status'] == 'processed'):
                message = 'Express Payout of amount '+str(transactionValue['amount'])+' for ' + str(
                    transactionValue['extraData']['customerId']) + ' is successful. Transaction id of this transaction is '+str(request.json['transactionId'])
                if ((transactionValue['serviceType'] == 'payoutUPI' ) or (transactionValue['serviceType'] == 'payoutUPI')):
                    if (transactionValue['extraData']['dailyPayoutTime']):
                        if (datetime.datetime.now().strftime("%d/%m/%Y") != transactionValue['extraData']['dailyPayoutTime']):
                            commissionManager.setCommission(transactionValue, request.json['uid'])
                    # get date in dd/mm/yyyy format
                fs.collection('users').document(request.json['uid']).update({"dailyPayoutTime": datetime.datetime.now().strftime("%d/%m/%Y")})
                transactionInstance.completeTransaction(
                    request.json['uid'], request.json['transactionId'], message, 'expressPayout', responseData[0])
                return {"success": "Payout created successfully","data":responseData}, 200
            elif (responseData[0]['status'] == 'cancelled' or responseData[0]['status'] == 'reversed'):
                message = 'Express Payout of amount '+str(transactionValue['amount'])+' for ' + str(
                    transactionValue['extraData']['customerId']) + ' is failed. Transaction id of this transaction is '+str(request.json['transactionId'])
                transactionInstance.failedTransaction(
                    request.json['uid'], request.json['transactionId'], message, 'expressPayout', responseData[0])
                return {"failed": "Payout cancelled","data":responseData}, 200
            return responseData, 200
        except Exception as e:
            ## logging.error(e)
            message = 'Express Payout of amount '+str(transactionValue['amount'])+' for ' + str(
                    transactionValue['extraData']['customerId']) + ' is failed. Transaction id of this transaction is '+str(request.json['transactionId'])
            transactionInstance.failedTransaction(
                    request.json['uid'], request.json['transactionId'], message, 'expressPayout', responseData[0])
            if DEVELOPMENT:
                return {'error': str(e)}, 400
            return {'error': 'Invalid token'}, 400
    else:
        return {'error': "We didn't received your data in json format"}, 400


@app.route('/payout/completeDailyPayout', methods=['POST'])
def completeDailyPayout():
    transactionValue = transactionInstance.getTransaction(
        request.json['uid'], request.json['transactionId'])
    if (transactionValue == None):
        return {'error': 'Transaction not found'}, 400
    if (not transactionInstance.checkBalance(transactionValue['amount'], request.json['uid'])):
        return {'error': 'Insufficient balance'}, 400

    if (request.is_json):
        if (transactionValue['extraData']['accountType'] is None):
            return {'error': 'accountType is required'}, 400
        if (transactionValue['extraData']['accountType'] == 'bank_account'):
            if (transactionValue['extraData']['account']['bankAccountName'] is None):
                return {'error': 'bankAccountName is required'}, 400
            if (transactionValue['extraData']['account']['ifsc'] is None):
                return {'error': 'ifsc is required'}, 400
            if (transactionValue['extraData']['account']['accountNumber'] is None):
                return {'error': 'accountNumber is required'}, 400
        elif (transactionValue['extraData']['accountType'] == 'vpa'):
            if (transactionValue['extraData']['account']['vpa'] is None):
                return {'error': 'vpa is required'}, 400
        elif (transactionValue['extraData']['accountType'] == 'card'):
            if (transactionValue['extraData']['account']['cardNumber'] is None):
                return {'error': 'cardNumber is required'}, 400
            if (transactionValue['extraData']['account']['cardName'] is None):
                return {'error': 'cardName is required'}, 400
        else:
            return {'error': 'Invalid accountType'}, 400
        if (transactionValue['extraData']['account']['name'] is None):
            return {'error': 'name is required'}, 400

        if (transactionValue['extraData']['account']['email'] is None):
            return {'error': 'email is required'}, 400

        if (transactionValue['extraData']['account']['contact'] is None):
            return {'error': 'contact is required'}, 400

        if (request.json['uid'] is None):
            return {'error': 'uid is required'}, 400

        if (transactionValue['extraData']['customerId'] is None):
            return {'error': 'customerId is required'}, 400

        if (transactionValue['idempotencyKey'] is None):
            return {'error': 'idempotencyKey is required'}, 400
        transactionValue['referenceId'] = request.json['transactionId']
        transactionValue['uid'] = request.json['uid']
        try:
            responseData = payout.quickPayout(
                transactionValue, transactionValue['extraData']['accountType'], transactionValue['idempotencyKey'])
            print("ACTUAL RESPONSE", responseData)
            if (responseData[0]['status'] == 'queued' or responseData[0]['status'] == 'pending' or responseData[0]['status'] == 'processing'):
                message = 'Payout of amount '+str(transactionValue['amount'])+' for ' + str(
                    transactionValue['extraData']['customerId']) + ' is pending. Transaction id of this transaction is '+str(request.json['transactionId'])
                transactionInstance.pendingTransaction(
                    request.json['uid'], request.json['transactionId'], message, 'expressPayout', responseData[0])
            elif (responseData[0]['status'] == 'processed'):
                message = 'Payout of amount '+str(transactionValue['amount'])+' for ' + str(
                    transactionValue['extraData']['customerId']) + ' is successful. Transaction id of this transaction is '+str(request.json['transactionId'])
                if ((transactionValue['serviceType'] == 'payoutUPI' ) or (transactionValue['serviceType'] == 'payoutUPI')):
                    if (datetime.datetime.now().strftime("%d/%m/%Y") != transactionValue['extraData']['dailyPayoutTime']):
                        commissionManager.setCommission(transactionValue, request.json['uid'])
                    # get date in dd/mm/yyyy format
                    fs.collection('users').document(request.json['uid']).update({"dailyPayoutTime": datetime.datetime.now().strftime("%d/%m/%Y")})
                transactionInstance.completeTransaction(
                    request.json['uid'], request.json['transactionId'], message, 'expressPayout', responseData[0])
            elif (responseData[0]['status'] == 'cancelled' or responseData[0]['status'] == 'reversed'):
                message = 'Payout of amount '+str(transactionValue['amount'])+' for ' + str(
                    transactionValue['extraData']['customerId']) + ' is failed. Transaction id of this transaction is '+str(request.json['transactionId'])
                transactionInstance.failedTransaction(request.json['uid'], request.json['transactionId'], message, 'expressPayout', responseData[0])
                return {"success": "Payout created successfully"}
            return responseData
        except Exception as e:
            message = 'Payout of amount '+str(transactionValue['amount'])+' for ' + str(
                transactionValue['extraData']['customerId']) + ' is failed. Transaction id of this transaction is '+str(request.json['transactionId'])
            transactionInstance.failedTransaction(request.json['uid'], request.json['transactionId'], message, 'expressPayout', responseData[0])
            ## logging.error(e)
            if DEVELOPMENT:
                return {'error': str(e)}, 400
            return {'error': 'Invalid token'}, 400
    else:
        return {'error': "We didn't received your data in json format"}, 400

# Messaging Services


@app.route('/messaging/sendSingleSMS', methods=['POST'])
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
            ## logging.error(e)
            return jsonify({'error': 'SMS request should contain phone number without (+91), message (<260 Chars) and priority (dnd/ndnd)' + e}), 400
        try:
            response = messaging.sendSingleSMS(message, phoneNo, priority)
            print(response.text)
            return jsonify({'success': response.text}), 200
        except Exception as e:
            ## logging.error(e)
            return jsonify({'error': str(e)}), 400
    else:
        return jsonify({'error': "We didn't received your data in json format "}), 400


@app.route('/messaging/sendMultipleSMS', methods=['POST'])
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
            ## logging.error(e)
            return jsonify({'error': 'SMS request should contain phone number without (+91), message (<260 Chars) and priority (dnd/ndnd)' + e}), 400
        try:
            response = messaging.sendMultiSMS(message, phoneNo, priority)
            return jsonify({'success': response.text}), 200
        except Exception as e:
            ## logging.error(e)
            return jsonify({'error': str(e)}), 400
    else:
        return jsonify({'error': "We didn't received your data in json format "}), 400


@app.route('/messaging/scheduleSMS', methods=['POST'])
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
            ## logging.error(e)
            return jsonify({'error': 'SMS request should contain phone number without (+91), message (<260 Chars) and priority (dnd/ndnd)' + e}), 400
        try:
            response = messaging.scheduleSMS(
                message, phoneNo, schedule, priority)
            return jsonify({'success': response.text}), 200
        except Exception as e:
            ## logging.error(e)
            return jsonify({'error': str(e)}), 400
    else:
        return jsonify({'error': "We didn't received your data in json format "}), 400


@app.route('/messaging/getSMSBalance', methods=['GET'])
def getSMSBalance():
    auth = authorize()
    if(auth[1] != 200):
        return jsonify(auth[0]), auth[1]
    try:
        response = messaging.getBalance()
        return jsonify({'success': response}), 200
    except Exception as e:
        ## logging.error(e)
        return jsonify({'error': str(e)}), 400


@app.route('/messaging/getMobileOperatorDetail', methods=['GET'])
def getMobileOperatorDetail():
    auth = authorize()
    if(auth[1] != 200):
        return jsonify(auth[0]), auth[1]
    try:
        response = messaging.getMobileOperatorDetail()
        return jsonify({'success': response}), 200
    except Exception as e:
        ## logging.error(e)
        return jsonify({'error': str(e)}), 400

# LPG services


@app.route('/lpg/getLpgOperators', methods=['POST'])
def getLpgOperatorList():
    auth = authorize()
    if(auth[1] != 200):
        return jsonify(auth[0]), auth[1]

    try:
        response = LpgInstance.getOperatorList(mode='online')
        return jsonify(response), 200
    except Exception as e:
        ## logging.error(e)
        return jsonify({'error': str(e)}), 400


@app.route('/lpg/fetchLpgDetails', methods=['POST'])
def fetchLpgDetails():
    auth = authorize()
    if(auth[1] != 200):
        return jsonify(auth[0]), auth[1]
    if (request.is_json):
        try:
            caNumber = request.json['customerNumber']
            operatorNo = request.json['operatorNumber']
        except Exception as e:
            ## logging.error(e)
            return jsonify({'error': "Please provide a customerNumber and operatorNumber ", "mainError": str(e)}), 400
        try:
            response = LpgInstance.fetchLpgDetails(caNumber, operatorNo)
            return response[0], response[1]
        except Exception as e:
            ## logging.error(e)
            return jsonify({'error': str(e)}), 400
    else:
        return jsonify({'error': "We didn't received your data in json format "}), 400


@app.route('/lpg/lpgRecharge', methods=['POST'])
def rechargeLpg():
    auth = authorize()
    if(auth[1] != 200):
        return jsonify(auth[0]), auth[1]
    if (request.is_json):
        transaction = transactionInstance.getTransaction(
            request.json['uid'], request.json['transactionId'])
        print("Transaction ", transaction)
        try:
            caNumber = transaction['extraData']['customerNumber']
            operatorNo = transaction['extraData']['operator']
            amount = transaction['amount']
            referenceId = request.json['transactionId']
            latitude = transaction['extraData']['latitude']
            longitude = transaction['extraData']['longitude']
        except Exception as e:
            ## logging.error(e)
            if DEVELOPMENT:
                print("Error ", e)
                return jsonify({"mainError": str(e)}), 400
            return {'error': "Please provide a customerNumber, operatorNumber, referenceId, latitude and longitude "}, 400
        try:
            response = LpgInstance.rechargeLpg(caNumber, operatorNo, amount, referenceId,
                                               latitude, longitude, transaction['extraData']['fields'], transaction['extraData'])
            if (response['status'] == True and response['response_code'] == 1):
                print("status", True,)
                message = 'LPG payment of amount '+str(amount)+' for ' + str(caNumber) + ' for operator ' + str(
                    operatorNo) + ' is successful. Transaction id of this transaction is '+str(referenceId)
                commissionManager.setCommission(transaction, request.json['uid'])
                transactionInstance.completeTransaction(
                    request.json['uid'], request.json['transactionId'], message, 'lpg', response)
                wallet.deduct_balance(request.json['uid'], amount)
            else:
                message = 'LPG payment of amount '+str(amount)+' for ' + str(caNumber) + ' for operator ' + str(
                    operatorNo) + ' is failed. Transaction id of this transaction is '+str(referenceId)
                transactionInstance.failedTransaction(
                    request.json['uid'], request.json['transactionId'], message, 'lpg', response)
            return jsonify(response), 200
        except Exception as e:
            ## logging.error(e)
            message = 'LPG payment of amount '+str(amount)+' for ' + str(caNumber) + ' for operator ' + str(
                    operatorNo) + ' is failed. Transaction id of this transaction is '+str(referenceId)
            transactionInstance.failedTransaction(
                    request.json['uid'], request.json['transactionId'], message, 'lpg', response)
            return jsonify({'error': str(e)}), 400

    else:
        return {'error': "We didn't received your data in json format "}, 400


@app.route('/lpg/lpgStatusInquiry', methods=['POST'])
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
            ## logging.error(e)
            return jsonify({'error': str(e)}), 400
    else:
        return jsonify({'error': "We didn't received your data in json format "}), 400

# HLR services


@app.route('/hlr/getCustomerInfo', methods=['POST'])
def getCustomerInfo():
    auth = authorize()
    if(auth[1] != 200):
        return jsonify(auth[0]), auth[1]
    if request.is_json:
        try:
            number = request.json['number']
            opType = request.json['type']
            response = HlrInstance.getOperator(number, opType)
            return response
        except Exception as e:
            ## logging.error(e)
            if DEVELOPMENT:
                print(e)
                return jsonify({'error': str(e)}), 400
            return jsonify({'error': 'Some error occurred from server side'}), 400
    else:
        return jsonify({'error': "We didn't received your data in json format "}), 400


@app.route('/hlr/getDthInfo', methods=['POST', 'GET'])
def getDthInfo():
    auth = authorize()
    if(auth[1] != 200):
        return jsonify(auth[0]), auth[1]
    if request.is_json:
        try:
            number = request.json['caNumber']
            opType = request.json['operator']
            response = HlrInstance.getDthInfo(number, opType)
            print("dth response", response)
            return response
        except Exception as e:
            ## logging.error(e)
            return jsonify({'error': str(e)}), 400
    else:
        return jsonify({'error': "We didn't received your data in json format "}), 400


@app.route('/hlr/getMobilePlan', methods=['POST'])
def getMobilePlan():
    auth = authorize()
    if(auth[1] != 200):
        return jsonify(auth[0]), auth[1]
    if request.is_json:
        try:
            circle = request.json['circle']
            operator = request.json['operator']
            response = HlrInstance.getPlanInfo(circle, operator)
            return response
        except Exception as e:
            ## logging.error(e)
            return jsonify({'error': str(e)}), 400
    else:
        return jsonify({'error': "We didn't received your data in json format "}), 400

# Recharge Services


@app.route('/recharge/getOperatorsList', methods=['POST'])
def getOperatorsList():
    # return False
    auth = authorize()
    if(auth[1] != 200):
        return jsonify(auth[0]), auth[1]
    return RechargeInstance.getOperatorList()


@app.route('/recharge/doRecharge', methods=['POST'])
def doRecharge():
    auth = authorize()
    if(auth[1] != 200):
        return jsonify(auth[0]), auth[1]
    if request.is_json:
        try:
            transactionData = transactionInstance.getTransaction(
                request.json['uid'], request.json['transactionId'])
            print("transactionData", transactionData)
            operator = transactionData['extraData']['operator']
            if not operator:
                return jsonify({'error': "Please provide operator"}), 400
            caNumber = int(transactionData['extraData']['caNumber'])
            if not caNumber:
                return jsonify({'error': "Please provide caNumber"}), 400
            amount = transactionData['amount']
            if not amount:
                return jsonify({'error': "Please provide amount"}), 400
            referenceId = request.json['transactionId']
            if not referenceId:
                return jsonify({'error': "Please provide referenceId"}), 400
            response = RechargeInstance.doRecharge(
                operator, caNumber, amount, referenceId)
            print("repsonse", response)
            startTime = time.time()
            print(time.time())
            if (response['status'] == True and response['response_code'] == 1):
                print("status", True,)
                message = 'Recharge of amount '+str(amount)+' for ' + str(
                    caNumber) + ' is successful. Transaction id of this transaction is '+str(referenceId)
                commissionManager.setCommission(transactionData, request.json['uid'])
                transactionInstance.completeTransaction(
                    request.json['uid'], request.json['transactionId'], message, 'recharge', response)
                wallet.deduct_balance(request.json['uid'], amount)
            else:
                message = 'Recharge of amount '+str(amount)+' for ' + str(
                    caNumber) + ' is failed. Transaction id of this transaction is '+str(referenceId)
                transactionInstance.failedTransaction(
                    request.json['uid'], request.json['transactionId'], message, 'recharge', response)
            print("recharge response", response,time.time() - startTime, time.time(), 'Time')
            
            return jsonify(response), 200
        except Exception as e:
            message = 'Recharge of amount '+str(amount)+' for ' + str(
                    caNumber) + ' is failed. Transaction id of this transaction is '+str(referenceId)
            transactionInstance.failedTransaction(
                    request.json['uid'], request.json['transactionId'], message, 'recharge', response)
            ## logging.error(e)
            return jsonify({'error': str(e)}), 400
    else:
        return jsonify({'error': "We didn't received your data in json format "}), 400


@app.route('/recharge/statusEnquiry', methods=['POST'])
def statusEnquiry():
    auth = authorize()
    if(auth[1] != 200):
        return jsonify(auth[0]), auth[1]
    if request.is_json:
        try:
            referenceId = request.json['referenceid']
            response = RechargeInstance.getStatusEnquiry(referenceId)
            return response, 200
        except Exception as e:
            ## logging.error(e)
            return jsonify({'error': str(e)}), 400
    else:
        return jsonify({'error': "We didn't received your data in json format "}), 400

@app.route('/recharge/callback')
def rechargeCallback():
    return jsonify({"status":200,"message":"Transaction completed successfully"}), 200

# BillPayment services


@app.route('/billPayment/getBillOperators', methods=['POST'])
def getBillOperators():
    auth = authorize()
    print("auth", auth)
    if(auth[1] != 200):
        return jsonify(auth[0]), auth[1]
    if request.is_json:
        try:
            response = BillPaymentInstance.getOperatorList('online')
            print("response", response)
            return jsonify(response), 200
        except Exception as e:
            ## logging.error(e)
            return jsonify({'error': str(e)}), 400
    else:
        return jsonify({'error': "We didn't received your data in json format "}), 400


@app.route('/billPayment/fetchBill', methods=['POST'])
def fetchBill():
    auth = authorize()
    if(auth[1] != 200):
        return jsonify(auth[0]), auth[1]
    if request.is_json:
        try:
            print(request.json)
            operatorNo = request.json['operator']
            caNumber = request.json['canumber']
            mode = request.json['mode']
            response = BillPaymentInstance.fetchBillDetails(
                operatorNo, caNumber, mode)
            print(response)
            return jsonify(response), 200
        except Exception as e:
            ## logging.error(e)
            return jsonify({'error': str(e)}), 400
    else:
        return jsonify({'error': "We didn't received your data in json format "}), 400


@app.route('/billPayment/payBill', methods=['POST'])
def payBill():
    auth = authorize()
    if(auth[1] != 200):
        return jsonify(auth[0]), auth[1]
    if request.is_json:
        try:
            transaction = transactionInstance.getTransaction(
                request.json['uid'], request.json['transactionId'])
            print("transaction", transaction)
            operatorNo = int(transaction['extraData']['operator']['id'])
            caNumber = transaction['extraData']['fields']['mainField']
            amount = transaction['amount']
            referenceId = request.json['transactionId']
            latitude = transaction['extraData']['latitude']
            longitude = transaction['extraData']['longitude']
            fetchedBill = transaction['extraData']['bill']['bill_fetch']
            response = BillPaymentInstance.payBill(
                operatorNo, caNumber, amount, referenceId, latitude, longitude, fetchedBill)
            print("response", response)
            if (response['status'] == True and response['response_code'] == 1):
                message = 'Bill payment of amount '+str(amount)+' for ' + str(
                    caNumber) + ' is successful. Transaction id of this transaction is '+str(referenceId)
                commissionManager.setCommission(transaction, request.json['uid'])
                transactionInstance.completeTransaction(
                    request.json['uid'], request.json['transactionId'], message, 'bbps', response)
                wallet.deductBalance(request.json['uid'], amount)
            else:
                message = 'Bill payment of amount '+str(amount)+' for ' + str(
                    caNumber) + ' is failed. Transaction id of this transaction is '+str(referenceId)
                transactionInstance.failedTransaction(
                    request.json['uid'], request.json['transactionId'], message, 'bbps', response)
            return jsonify(response), 200
        except Exception as e:
            message = 'Bill payment of amount '+str(amount)+' for ' + str(
                    caNumber) + ' is failed. Transaction id of this transaction is '+str(referenceId)
            transactionInstance.failedTransaction(
                    request.json['uid'], request.json['transactionId'], message, 'bbps', response)
            ## logging.error(e)
            return jsonify({'error': str(e)}), 400
    else:
        return jsonify({'error': "We didn't received your data in json format "}), 400


@app.route('/billPayment/billStatusEnquiry',methods=['POST'])
def billStatusEnquiry():
    # auth = authorize()
    # if(auth[1] != 200):
    #     return jsonify(auth[0]), auth[1]
    if request.is_json:
        try:
            referenceId = request.json['referenceid']
            response = BillPaymentInstance.statusEnquiry(referenceId)
            return jsonify(response), 200
        except Exception as e:
            ## logging.error(e)
            return jsonify({'error': str(e)}), 400
    else:
        return jsonify({'error': "We didn't received your data in json format "}), 400

@app.route('/billPayment/callback', methods=['POST'])
def billCallback():
    return {"status":200,"message":"Transaction completed successfully"},200

# LIC services


@app.route('/lic/fetchLicBill', methods=['POST'])
def fetchLicBill():
    auth = authorize()
    if(auth[1] != 200):
        return jsonify(auth[0]), auth[1]
    if request.is_json:
        try:
            caNumber = request.json['caNumber']
            email = request.json['email']
            mode = 'online'
            response = LicInstance.fetchLicBill(caNumber, email, mode)
            return response
        except Exception as e:
            ## logging.error(e)
            return jsonify({'error': str(e)}), 400
    else:
        return jsonify({'error': "We didn't received your data in json format "}), 400


@app.route('/lic/payLicBill', methods=['POST'])
def payLicBill():
    auth = authorize()
    if(auth[1] != 200):
        return jsonify(auth[0]), auth[1]
    if request.is_json:
        try:
            transaction = transactionInstance.getTransaction(
                request.json['uid'], request.json['transactionId'])
            caNumber = transaction['extraData']['formData']['caNumber']
            amount = float(transaction['amount'])
            email = transaction['extraData']['formData']['email']
            latitude = transaction['extraData']['latitude']
            longitude = transaction['extraData']['longitude']
            mode = 'online'
            referenceId = request.json['transactionId']
            billFetch = transaction['extraData']['bill']
            response = LicInstance.payLicBill(
                caNumber, mode, amount, email, referenceId, latitude, longitude, billFetch)
            print(response)
            if (response['status'] == True and response['response_code'] == 1):
                message = 'Lic payment of amount '+str(amount)+' for ' + str(
                    caNumber) + ' is successful. Transaction id of this transaction is '+str(referenceId)
                commissionManager.setCommission(transaction, request.json['uid'])
                transactionInstance.completeTransaction(
                    request.json['uid'], request.json['transactionId'], message, 'lic', response)
                wallet.deduct_balance(request.json['uid'], amount)
            else:
                message = 'Lic payment of amount '+str(amount)+' for ' + str(
                    caNumber) + ' is failed. Transaction id of this transaction is '+str(referenceId)
                transactionInstance.failedTransaction(
                    request.json['uid'], request.json['transactionId'], message, 'lic', response)
            return response
        except Exception as e:
            message = 'Lic payment of amount '+str(amount)+' for ' + str(
                    caNumber) + ' is failed. Transaction id of this transaction is '+str(referenceId)
            transactionInstance.failedTransaction(
                    request.json['uid'], request.json['transactionId'], message, 'lic', response)
            ## logging.error(e)
            print(e)
            return jsonify({'error': str(e)}), 400
    else:
        return jsonify({'error': "We didn't received your data in json format "}), 400


@app.route('/lic/getLicStatus', methods=['POST'])
def LicStatus():
    auth = authorize()
    if(auth[1] != 200):
        return jsonify(auth[0]), auth[1]
    if request.is_json:
        try:
            referenceId = request.json['referenceid']
            response = LicInstance.getLicStatus(referenceId)
            return response
        except Exception as e:
            ## logging.error(e)
            return jsonify({'error': str(e)}), 400
    else:
        return jsonify({'error': "We didn't received your data in json format "}), 400

# FastTag services


@app.route('/fastTag/getFastTagOperatorList', methods=['POST'])
def getFastTagOperatorList():
    auth = authorize()
    if(auth[1] != 200):
        return jsonify(auth[0]), auth[1]
    if request.is_json:
        try:
            response = FastTagInstance.getOperatorsList()
            return jsonify(response), 200
        except Exception as e:
            ## logging.error(e)
            return jsonify({'error': str(e)}), 400
    else:
        return jsonify({'error': "We didn't received your data in json format "}), 400


@app.route('/fastTag/fastTagDetails', methods=['POST'])
def fastTagDetails():
    auth = authorize()
    if(auth[1] != 200):
        return jsonify(auth[0]), auth[1]
    if request.is_json:

        try:
            operatorNo = request.json['operator']
            caNumber = request.json['caNumber']
            response = FastTagInstance.fetchConsumerDetails(
                operatorNo, caNumber)
            return jsonify(response), 200
        except Exception as e:
            ## logging.error(e)
            return jsonify({'error': str(e)}), 400
    else:
        return jsonify({'error': "We didn't received your data in json format "}), 400


@app.route('/fastTag/rechargeFastTag', methods=['POST'])
def rechargeFastTag():
    auth = authorize()
    if(auth[1] != 200):
        return jsonify(auth[0]), auth[1]
    if request.is_json:
        print(request.json)
        transaction = transactionInstance.getTransaction(
            request.json['uid'], request.json['transactionId'])
        print("TRANSACTION ", transaction)
        try:
            operatorNo = int(transaction['extraData']['bank']['id'])
            caNumber = transaction['extraData']['caNumber']
            amount = transaction['amount']
            latitude = transaction['extraData']['latitude']
            longitude = transaction['extraData']['longitude']
            referenceId = request.json['transactionId']
            bill_fetch = transaction['extraData']['bill_fetch']
            response = FastTagInstance.recharge(
                operatorNo, caNumber, amount, referenceId, latitude, longitude, bill_fetch)
            print(response)
            if (response['status'] == True and response['response_code'] == 1):
                message = 'FastTag payment of amount '+str(amount)+' for ' + str(
                    caNumber) + ' is successful. Transaction id of this transaction is '+str(referenceId)
                commissionManager.setCommission(transaction, request.json['uid'])
                transactionInstance.completeTransaction(
                    request.json['uid'], request.json['transactionId'], message, 'fastTag', response)
                wallet.deduct_balance(request.json['uid'], amount)
            else:
                message = 'FastTag payment of amount '+str(amount)+' for ' + str(
                    caNumber) + ' is failed. Transaction id of this transaction is '+str(referenceId)
                transactionInstance.failedTransaction(
                    request.json['uid'], request.json['transactionId'], message, 'fastTag', response)
            return jsonify(response), 200
        except Exception as e:
            message = 'FastTag payment of amount '+str(amount)+' for ' + str(
                    caNumber) + ' is failed. Transaction id of this transaction is '+str(referenceId)
            transactionInstance.failedTransaction(
                    request.json['uid'], request.json['transactionId'], message, 'fastTag', response)
            ## logging.error(e)
            return jsonify({'error': str(e)}), 400


@app.route('/fastTag/getFastTagStatus', methods=['POST'])
def getFastTagStatus():
    auth = authorize()
    if(auth[1] != 200):
        return jsonify(auth[0]), auth[1]
    if request.is_json:
        try:
            referenceId = request.json['referenceid']
            response = FastTagInstance.getFastTagStatus(referenceId)
            return jsonify(response), 200
        except Exception as e:
            ## logging.error(e)
            return jsonify({'error': str(e)}), 400
    else:
        return jsonify({'error': "We didn't received your data in json format "}), 400

# UTM services


@app.route('/digitalAccount/getAccountReferralLink', methods=['POST'])
def getAccountReferralLink():
    auth = authorize()
    if(auth[1] != 200):
        return jsonify(auth[0]), auth[1]
    try:
        response = HlrInstance.getUTMAccountLInk()
        print(response)
        return jsonify(response), 200
    except Exception as e:
        ## logging.error(e)
        return jsonify({'error': str(e)}), 400

# Admin Services


@app.route('/admin/blockUser', methods=['POST'])
def blockUser():
    print(request.json)
    auth = authorize()
    if(auth[1] != 200):
        return jsonify(auth[0]), auth[1]
    if (request.is_json):
        try:
            statement = userManagement.blockUser(
                request.json, request.json['blockID'])
            print(statement)
            return statement
        except Exception as e:
            ## logging.error(e)
            if DEVELOPMENT:
                return jsonify({'error': str(e)}), 400
            return jsonify({'error': "We didn't received your data in json format "}), 400


@app.route('/admin/unblockUser', methods=['POST'])
def unblockUser():
    auth = authorize()
    if(auth[1] != 200):
        return jsonify(auth[0]), auth[1]
    if (request.is_json):
        try:
            return userManagement.unblockUser(request.json['uid'], request.json['blockID'])
        except Exception as e:
            ## logging.error(e)
            if DEVELOPMENT:
                return jsonify({'error': str(e)}), 400
            return jsonify({'error': "We didn't received your data in json format "}), 400


@app.route('/admin/deleteUser', methods=['POST'])
def deleteUser():
    auth = authorize()
    if(auth[1] != 200):
        return jsonify(auth[0]), auth[1]
    if (request.is_json):
        try:
            userName = request.json
            return userManagement.deleteUser(request.json['uid'], request.json['deleteUserId'])
        except Exception as e:
            ## logging.error(e)
            if DEVELOPMENT:
                return jsonify({'error': str(e)}), 400
            return jsonify({'error': "We didn't received your data in json format "}), 400
    else:
        return jsonify({'error': "We didn't received your data in json format "}), 400


@app.route('/admin/changeAccess', methods=['POST'])
def changeAccess():
    print("ISJSON", request.is_json, request.json)
    auth = authorize()
    if(auth[1] != 200):
        return jsonify(auth[0]), auth[1]
    else:
        print('Authorization passed')
    if (request.is_json):
        try:
            statement = userManagement.changeAccess(
                request.json['changeAccessLevel'], request.json['changeUserId'], request.json['uid'])
            print("statement", statement)
            return statement
        except Exception as e:
            ## logging.error(e)
            if DEVELOPMENT:
                return jsonify({'error': str(e)}), 400
            return jsonify({'error': "An error occurred "}), 400
    else:
        return jsonify({'error': "We didn't received your data in json format "}), 400


@app.route('/admin/createUser', methods=['POST'])
def createUser():
    auth = authorize()
    if(auth[1] != 200):
        return jsonify(auth[0]), auth[1]
    if request.is_json:
        try:
            print(request.json)
            return userManagement.createUser(request.json)
        except Exception as e:
            ## logging.error(e)
            print(e)
            if DEVELOPMENT:
                return jsonify({'error': str(e)}), 400
            return jsonify({'error': "We didn't received your data in json format "}), 400
    else:
        return jsonify({'error': "We didn't received your data in json format "}), 400


@app.route('/admin/getTransactions', methods=['POST'])
def getTransactions():
    auth = authorize()
    if(auth[1] != 200):
        return jsonify(auth[0]), auth[1]
    if request.is_json:
        try:
            print(request.json)
            return transactionInstance.getTransactions(request.json['type'], request.json['startDate'], request.json['endDate'])
        except Exception as e:
            ## logging.error(e)
            print(e)
            if DEVELOPMENT:
                return jsonify({'error': str(e)}), 400
            return jsonify({'error': "We didn't received your data in json format "}), 400
    else:
        return jsonify({'error': "We didn't received your data in json format "}), 400


# Aeps Services


@app.route('/aeps/bankList', methods=['POST'])
def getAepsBankList():
    # print(request.is_json,request.json)
    auth = authorize()
    if(auth[1] != 200):
        return jsonify(auth[0]), auth[1]
    if (not request.is_json):
        return {'error': "We didn't received your data in json format "}, 400
    try:
        response = aeps.getBankList()
        # print(response,response.text)
        if (response.json()['response_code'] == 1):
            return response.json(), 200
        else:
            if DEVELOPMENT:
                return jsonify({'error': response.json()['message']}), 400
            return jsonify({'error': "Cannot fetch bank list."}), 400
    except Exception as e:
        ## logging.error(e)
        if DEVELOPMENT:
            return jsonify({'error': str(e)}), 400
        else:
            return jsonify({'error': "Some error occurred"}), 400


@app.route('/aeps/test/balanceEnquiry',methods=['POST','GET'])
def testBalanceEnquiry():
    auth = authorize()
    if(auth[1] != 200):
        return jsonify(auth[0]), auth[1]
    #logging.error(request.json)
    # return {'responding':True}
    print(request)
    print(request.json)
    if (not request.is_json):
        return jsonify({'error': "We didn't received your data in json format "}), 400
    try:
        print("request.is_json",request.is_json)
        #logging.info(request.json)
        response = aeps.getBalanceEnquiry(
            request.json['latitude'],
            request.json['longitude'],
            request.json['mobile_number'],
            request.json['referenceNo'],
            request.json['adhaarNumber'],
            request.json['nationalBankIdentification'],
            request.json['requestRemarks'],
            request.json['data'].strip(),
            request.json['is_iris'],
            request.json['merchantCode']
        )
        #logging.info(response[0])
        print(response)
        return response
    except Exception as e:
        #logging.error(e)
        print(e)
        if DEVELOPMENT:
            return jsonify({'error': str(e)}), 400
        else:
            return jsonify({'error': "Some error occurred"}), 400

@app.route('/aeps/balanceEnquiry', methods=['POST'])
def getAepsBalanceEnquiry():
    auth = authorize()
    if(auth[1] != 200):
        return jsonify(auth[0]), auth[1]
    if (not request.is_json):
        return jsonify({'error': "We didn't received your data in json format "}), 400
    try:
        requestData = request.json
        mainTransactionData = transactionInstance.getTransaction(
            requestData['uid'], requestData['transactionId'])['extraData']
        transactionData = mainTransactionData['aepsData']
        transactionData['data'] = transactionData['data'].replace('{PID=', '')
        transactionData['data'] = transactionData['data'].replace('}', '')
        response = aeps.getBalanceEnquiry(
            transactionData['latitude'],
            transactionData['longitude'],
            transactionData['mobile_number'],
            transactionData['referenceNo'],
            transactionData['adhaarNumber'],
            transactionData['nationalBankIdentification'],
            transactionData['requestRemarks'],
            transactionData['data'].strip(),
            transactionData['is_iris'],
            mainTransactionData['merchantCode']
        )
        print(response)
        ## logging.info(response)
        if (response[2] and response[0]['response_code'] == 1 and response[1] == 200):
            message = 'Balance Enquiry is fetched for ' + str(response[0]['clientrefno']) + ' is successful. Transaction id of this transaction is '+str(request.json['transactionId'])
            commissionManager.setCommission(mainTransactionData, request.json['uid'])
            transactionInstance.completeTransaction(request.json['uid'], request.json['transactionId'], message, 'fastTag', response[0])
            return response
        else:
            transactionInstance.failedTransaction(request.json['uid'], request.json['transactionId'], response[0])
            if DEVELOPMENT:
                return jsonify({'error': response[0]['message']}), 400
            return jsonify({'error': "An error occurred","data":response}), 400
    except Exception as e:
        #logging.error(e)
        transactionInstance.failedTransaction(request.json['uid'], request.json['transactionId'], response[0])
        print(e)
        if DEVELOPMENT:
            return jsonify({'error': str(e)}), 400
        else:
            return jsonify({'error': "Some error occurred"}), 400


@app.route('/aeps/cashWithdrawal', methods=['POST'])
def getAepsCashWithDrawl():
    auth = authorize()
    if(auth[1] != 200):
        return jsonify(auth[0]), auth[1]
    if (not request.is_json):
        return jsonify({'error': "We didn't received your data in json format "}), 400
    try:
        jsonData = request.json
        mainTransactionData = transactionInstance.getTransaction(
            jsonData['uid'], jsonData['transactionId'])
        print(mainTransactionData)
        transactionData = mainTransactionData['extraData']['aepsData']
        transactionData['data'] = transactionData['data'].replace('{PID=', '')
        transactionData['data'] = transactionData['data'].replace('}', '')
        response = aeps.withdrawCash(
            transactionData['latitude'],
            transactionData['longitude'],
            transactionData['mobile_number'],
            transactionData['referenceNo'],
            transactionData['adhaarNumber'],
            transactionData['nationalBankIdentification'],
            transactionData['requestRemarks'],
            transactionData['data'],
            mainTransactionData['amount'],
            transactionData['is_iris'],
            mainTransactionData['extraData']['merchantCode']
        )
        print(response[0])
        if (response[2] and response[0]['response_code'] == 1 and response[1] == 200):
            wallet.add_balance(jsonData['uid'], mainTransactionData['amount'])
            message = 'Cash Withdrawal for ' + str(response[0]['clientrefno']) + ' of ' + str(mainTransactionData['amount']) + ' is successful. Transaction id of this transaction is '+str(request.json['transactionId'])
            commissionManager.setCommission(mainTransactionData, request.json['uid'])
            transactionInstance.completeTransaction(jsonData['uid'], jsonData['transactionId'], message, 'fastTag', response[0])
            aeps.withdrawThreeWay(response[0]['clientrefno'],'success')
            return response
        elif (response[2]):
            transactionInstance.failedTransaction(jsonData['uid'], jsonData['transactionId'], response[0])
            if (response[0]['response_code'] == 0 and response[0]['status']):
                aeps.withdrawThreeWay(response[0]['clientrefno'],'failed')
            if DEVELOPMENT:
                return jsonify({'error': response[0]['message']}), 400
            return jsonify({'error': "An error occurred","data":response}), 400
        else:
            return jsonify({'error': "An error occurred","data":response}), 400
    except Exception as e:
        #logging.error(e)
        transactionInstance.failedTransaction(jsonData['uid'], jsonData['transactionId'], response[0])
        if DEVELOPMENT:
            return jsonify({'error': str(e)}), 400
        return jsonify({'error': "We didn't received your data in json format "}), 400


@app.route('/aeps/miniStatement', methods=['POST'])
def miniStatement():
    auth = authorize()
    if(auth[1] != 200):
        return jsonify(auth[0]), auth[1]
    if (not request.is_json):
        return jsonify({'error': "We didn't received your data in json format "}), 400
    try:
        jsonData = request.json
        mainTransactionData = transactionInstance.getTransaction(
            jsonData['uid'], jsonData['transactionId'])['extraData']
        transactionData = mainTransactionData['aepsData']
        transactionData['data'] = transactionData['data'].replace('{PID=', '')
        transactionData['data'] = transactionData['data'].replace('}', '')
        response = aeps.getMiniStatement(
                transactionData['latitude'],
            transactionData['longitude'],
            transactionData['mobile_number'],
            transactionData['referenceNo'],
            transactionData['adhaarNumber'],
            transactionData['nationalBankIdentification'],
            transactionData['requestRemarks'],
            transactionData['data'],
            transactionData['is_iris'],
            mainTransactionData['merchantCode']
        )
        print(response)
        logging.info(response)
        if (response[2] and response[0]['response_code'] == 1 and response[1] == 200):
            message = 'Mini Statement is fetched for ' + str(response['clientrefno']) + ' is successful. Transaction id of this transaction is '+str(request.json['transactionId'])
            commissionManager.setCommission(mainTransactionData, request.json['uid'])
            transactionInstance.completeTransaction(request.json['uid'], request.json['transactionId'], message, 'fastTag', response)
            return response
        else:
            transactionInstance.failedTransaction(request.json['uid'], request.json['transactionId'], response)
            if DEVELOPMENT:
                return jsonify({'error': response[0]['message']}), 400
            return jsonify({'error': "An error occurred","data":response}), 400
    except Exception as e:
        logging.error(e)
        transactionInstance.failedTransaction(request.json['uid'], request.json['transactionId'], response)
        if DEVELOPMENT:
            return jsonify({'error': str(e)}), 400
        return jsonify({'error': "We didn't received your data in json format "}), 400


@app.route('/aeps/getWithdrawStatus', methods=['POST'])
def getWithdrawStatus():
    auth = authorize()
    if(auth[1] != 200):
        return jsonify(auth[0]), auth[1]
    if (not request.is_json):
        return jsonify({'error': "We didn't received your data in json format "}), 400
    try:
        jsonData = request.json
        response = aeps.getCashWithdrawStatus(jsonData['referenceNo'])
        print(response)
        if (response[1] == 200 and response[0]['response_code'] == 1):
            return response
        else:
            ## logging.error(response[0])
            if DEVELOPMENT:
                return jsonify({'error': response[0]['message']}), 400
            return jsonify({'error': "An error occurred"}), 400
    except Exception as e:
        ## logging.error(e)
        if DEVELOPMENT:
            return jsonify({'error': str(e)}), 400
        return jsonify({'error': "We didn't received your data in json format "}), 400


@app.route('/aeps/withdrawThreeWay', methods=['POST'])
def withdrawThreeWay():
    auth = authorize()
    if(auth[1] != 200):
        return jsonify(auth[0]), auth[1]
    if (not request.is_json):
        return jsonify({'error': "We didn't received your data in json format "}), 400
    try:
        jsonData = request.json
        response = aeps.withdrawThreeWay(
            jsonData['reference'], jsonData['status'])
        print(response)
        if (response[2] and response[0]['response_code'] == 1 and response[1] == 200):
            ## logging.info(response)
            return response
        else:
            ## logging.error(response)
            if DEVELOPMENT:
                return jsonify({'error': response[0]['message']}), 400
            return jsonify({'error': "An error occurred"}), 400
    except Exception as e:
        ## logging.error(e)
        if DEVELOPMENT:
            return jsonify({'error': str(e)}), 400
        return jsonify({'error': "We didn't received your data in json format "}), 400


@app.route('/aeps/aadhaarPay', methods=['POST'])
def aadhaarPay():
    auth = authorize()
    if(auth[1] != 200):
        return jsonify(auth[0]), auth[1]
    if (not request.is_json):
        return jsonify({'error': "We didn't received your data in json format "}), 400
    try:
        jsonData = request.json
        mainTransactionData = transactionInstance.getTransaction(
            jsonData['uid'], jsonData['transactionId'])['extraData']
        transactionData = mainTransactionData['aepsData']
        transactionData['data'] = transactionData['data'].replace('{PID=', '')
        transactionData['data'] = transactionData['data'].replace('}', '')
        response = aeps.aadhaarPay(
                transactionData['latitude'],
            transactionData['longitude'],
            transactionData['mobile_number'],
            transactionData['referenceNo'],
            transactionData['adhaarNumber'],
            transactionData['nationalBankIdentification'],
            transactionData['requestRemarks'],
            transactionData['data'],
            transactionData['is_iris'],
            mainTransactionData['merchantCode']
        )
        print(response)
        #logging.info(response)
        if (response[2] and response[0]['response_code'] == 1 and response[1] == 200):
            message = 'Aadhaar Pay done for ' + str(response['clientrefno']) + ' is successful. Transaction id of this transaction is '+str(request.json['transactionId'])
            commissionManager.setCommission(mainTransactionData, request.json['uid'])
            transactionInstance.completeTransaction(request.json['uid'], request.json['transactionId'], message, 'fastTag', response)
            return response
        else:
            transactionInstance.failedTransaction(request.json['uid'], request.json['transactionId'], response)
            if DEVELOPMENT:
                return jsonify({'error': response[0]['message']}), 400
            return jsonify({'error': "An error occurred"}), 400
    except Exception as e:
        transactionInstance.failedTransaction(request.json['uid'], request.json['transactionId'], response)
        ## logging.error(e)
        if DEVELOPMENT:
            return jsonify({'error': str(e)}), 400
        return jsonify({'error': "We didn't received your data in json format "}), 400


@app.route('/aeps/aadhaarPayStatus', methods=['POST'])
def aadhaarPayStatus():
    auth = authorize()
    if(auth[1] != 200):
        return jsonify(auth[0]), auth[1]
    if (not request.is_json):
        return jsonify({'error': "We didn't received your data in json format "}), 400
    try:
        jsonData = request.json
        response = aeps.aadhaarPayStatus(jsonData['referenceId'])
        print(response)
        if (response[2] and response[0]['response_code'] == 1 and response[1] == 200):
            return response
        else:
            ## logging.error(response)
            if DEVELOPMENT:
                return jsonify({'error': response.json()['message']}), 400
            return jsonify({'error': "An error occurred"}), 400
    except Exception as e:
        ## logging.error(e)
        if DEVELOPMENT:
            return jsonify({'error': str(e)}), 400
        return jsonify({'error': "We didn't received your data in json format "}), 400


@app.route('/qr/registerQr', methods=['POST'])
def registerQr():
    auth = authorize()
    if(auth[1] != 200):
        return jsonify(auth[0]), auth[1]
    try:
        response = qr.generateQr(
            request.json['storeName'], request.json['uid'])
        print(response, response.text)
        return response.json(), 200
        # if (response.json()['response_code'] == 1):
        # else:
        #     if DEVELOPMENT:
        #         return jsonify({'error': response.json()['message']}), 400
        #     return jsonify({'error': "An error occurred"}), 400
    except Exception as e:
        ## logging.error(e)
        if DEVELOPMENT:
            return jsonify({'error': str(e)}), 400
        return jsonify({'error': "We didn't received your data in json format "}), 400

@app.route('/onboarding/setup', methods=['POST'])
def onboardingSetup():
    print(request)
    print(request.json)
    auth = authorize()
    if(auth[1] != 200):
        return jsonify(auth[0]), auth[1]
    try:
        if (not request.is_json):
            return jsonify({'error': "We didn't received your data in json format "}), 400
        getUser = transactionInstance.getUser(request.json['uid'])
        print(getUser)
        #logging.error(getUser)
        response = onboarding.onboardingWebOld(
            getUser['userId'],
            getUser['phoneNumber'],
            0,
            getUser['email'],
            request.json['uid'],
        )
        print(response)
        ## logging.error(response)
        return response, 200
    except Exception as e:
        ## logging.error(e)
        if DEVELOPMENT:
            return jsonify({'error': str(e)}), 400
        return jsonify({'error': "Some error occurred"}), 400


@app.route('/onboarding/status',methods = ['POST'])
def checkOnboardingStatus():
    auth = authorize()
    if(auth[1] != 200):
        return jsonify(auth[0]), auth[1]
    try:
        if (not request.is_json):
            return jsonify({'error': "We didn't received your data in json format "}), 400
        getUser = transactionInstance.getUser(request.json['uid'])
        print(getUser)
        #logging.error(getUser)
        response = onboarding.checkStatus(request.json)
        print(response)
        ## logging.error(response)
        return response
    except Exception as e:
        ## logging.error(e)
        if DEVELOPMENT:
            return jsonify({'error': str(e)}), 400
        return jsonify({'error': "Some error occurred"}), 400

@app.route('/onboarding/callback', methods=['POST'])
def onboardingCallback():
    return {"status": 200, "message": "Transaction completed successfully"}
    # auth = authorize()
    # if(auth[1] != 200):
    #     return jsonify(auth[0]), auth[1]
    # try:
    #     if (request.view_args['data']):
    #         response = onboarding.decodeCallbackData(request.view_args['data'])
    #         print(response)
    #         return response
    # except Exception as e:
    #logging.error(e)
    #     if DEVELOPMENT:
    #         return jsonify({'error': e}), 400
    #     return jsonify({'error': "We didn't received your data in json format "}), 400

@app.route('/razorpay/callback', methods=['POST'])
def razorpayCallback():
    print(request.json)
    verifier = "ybiuh83r9823e98uy7B67rF57667TV&rtV8^&T547^Tfdgio384093hniu7^t^&t&^T&t869*789&987u9808K09*90U98yvR54edc43X43dF76v&^T&^"
    print({"data":request.data.decode(),"type":type(request.data.decode()),"header":request.headers.get('X-Razorpay-Signature'),"verifier":verifier})
    res = client.utility.verify_webhook_signature(request.data.decode(), request.headers.get('X-Razorpay-Signature'), verifier)
    print(res)
    if(res):
        if (request.json["event"].startswith('payout.') and request.json["event"]!='payout.updated'):
            fs.collection("users").document(request.json["payload"]["payout"]["entity"]["notes"]["userId"]).collection("transaction").document(request.json["payload"]["payout"]["entity"]["reference_id"]).update({"newPayoutStatus":{**request.json["payload"]["payout"]["entity"],"event":request.json["event"]}})
            if (request.json["event"]=='payout.processed'):
                wallet.deduct_balance(request.json["payload"]["payout"]["entity"]["notes"]["userId"],request.json["payload"]["payout"]["entity"]["amount"]/100)
    return {"done":True,"status":200}

@app.route('/upi/createPayment', methods=['POST'])
def createPayment():
    auth = authorize()
    if(auth[1] != 200):
        return jsonify(auth[0]), auth[1]
    try:
        requestData = request.json
        print("requestData",requestData)
        if (not request.is_json):
            return jsonify({'error': "We didn't received your data in json format "}), 400
        mainTransactionData = transactionInstance.getTransaction(
            requestData['uid'], requestData['transactionId'])
        print("mainTransactionData",mainTransactionData)
        response = upi.createOrder(mainTransactionData['amount'], requestData['transactionId'], mainTransactionData['extraData']
                                     ['customerName'], mainTransactionData['extraData']['customerEmail'], mainTransactionData['extraData']['customerMobile'], requestData['uid'])
        # print(response)
        return response, 200
    except Exception as e:
        ## logging.error(e)
        if DEVELOPMENT:
            return jsonify({'error': e}), 400
        return jsonify({'error': "We didn't received your data in json format "}), 400


@app.route('/upi/status', methods=['POST'])
def qrStatus():
    try:
        response = upi.checkStatus(request.json['transactionId'],request.json['date'])
        print(response, response.json())
        if (response.json()['status']==True):
            message = "Your upi transaction " + \
                request.json['transactionId'] + " is successful"
            transactionInstance.completeTransaction(request.json['uid'],request.json['transactionId'],message,'qr',response.json())
            return response.json(), 200
        else:
            transactionInstance.failedTransaction(request.json['uid'],request.json['transactionId'],response.json())
            return response.json(), 400
    except Exception as e:
        transactionInstance.failedTransaction(request.json['uid'],request.json['transactionId'],response.json())
        ## logging.error(e)
        if DEVELOPMENT:
            return jsonify({'error': str(e)}), 400
        return jsonify({'error': "We didn't received your data in json format "}), 400

@app.route('/sms/send',methods=['POST','GET'])
def sendSMS():
    res = messaging.sendSingleSMS("123456 is your OTP for Login. OTP valid for 10 minutes. Regards SSSPAY","9517457296","ndnd")
    print(res)
    if (res):
        print(res.content)
    return "DONE"


@app.route('/commission',methods=['POST','GET'])
def commission():
    data = fs.collection("users").document("YpBrnCoe4laoeY1RmTCZ4pupOys2d").collection("transaction").document("0GSa6y4jz9RSuGOgZ0Kj").get()
    return commissionManager.setCommision(data.to_dict(),"YpBrnCoe4laoeY1RmTCZ4pupOys2")
    # return commisionManager.setCommision('0GSa6y4jz9RSuGOgZ0Kj','YpBrnCoe4laoeY1RmTCZ4pupOys2','aeps','17rwVDDLspUNGRgQUYA6')


@app.route('/resetPassword/generateOtp',methods=['POST'])
def generateOtp():
    try:
        requestData = request.json
        print("requestData",requestData)
        if (not request.is_json):
            return jsonify({'error': "We didn't received your data in json format "}), 400
        if (not requestData['mobile']):
            return jsonify({'error': "Mobile number is required"}), 400
        otp = random.randint(100000, 999999)
        previousOtp = fs.collection("otpData").document(requestData['mobile']).get()
        if(previousOtp.exists and previousOtp.to_dict()['otp']):
            otp = previousOtp.to_dict()['otp']
        else:
            doc = fs.collection("otpData").document(requestData['mobile']).set({"otp":otp})
        res = messaging.sendOtp(otp,requestData['mobile'])
        if (res):
            print(res.content)
            return jsonify({"status":("Otp is sent to {}").format("******"+str(requestData['mobile'])[6:10])}), 200
        else:
            return jsonify({'error': "We didn't received your data in json format "}), 400
    except Exception as e:
        ## logging.error(e)
        if DEVELOPMENT:
            return jsonify({'error': str(e)}), 400
        return jsonify({'error': "We didn't received your data in json format "}), 400

@app.route('/resetPassword/verifyOtp',methods=['POST'])
def verifyOtp():
    try:
        requestData = request.json
        if (not request.is_json):
            return jsonify({'error': "We didn't received your data in json format "}), 400
        if (not requestData['otp']):
            return jsonify({'error': "Otp is required"}), 400
        previousOtp = fs.collection("otpData").document(requestData['mobile']).get()
        if(str(previousOtp.to_dict()['otp']) == str(requestData['otp'])):
            previousOtp = fs.collection("otpData").document(requestData['mobile']).update({"otp":None})
            return jsonify({"status":"OTP is verified."}), 200
        else:
            return jsonify({"error":"Incorrect OTP entered."}), 400
    except Exception as e:
        ## logging.error(e)
        if DEVELOPMENT:
            return jsonify({'error': e}), 400
        return jsonify({'error': "We didn't received your data in json format "}), 400

@app.route('/resetPassword/checkEmailPhone',methods=['POST'])
def checkEmail():
    # check if email or the phone exists in users database
    try:
        requestData = request.json
        if (not request.is_json):
            return jsonify({'error': "We didn't received your data in json format "}), 400
            
        if ('email' in requestData.keys()):
            return userManagement.getUserByEmail(requestData['email'])
        elif ('mobile' in requestData.keys()):
            return userManagement.getUserByPhone('+91'+requestData['mobile'])
        else:
            return jsonify({'error': "Email or phone is required"}), 400
    except Exception as e:
        ## logging.error(e)
        if DEVELOPMENT:
            return jsonify({'error': e}), 400
        return jsonify({'error': "We didn't received your data in json format "}), 400


@app.route('/resetPassword',methods=['POST'])
def resetPassword():
    try:
        requestData = request.json
        if (not request.is_json):
            return jsonify({'error': "We didn't received your data in json format "}), 400
        if (not requestData['uid']):
            return jsonify({'error': "User id is required"}), 400
        if (not requestData['password']):
            return jsonify({'error': "Password is required"}), 400
        return userManagement.resetPassword(requestData['uid'],requestData['password'])
    except Exception as e:
        ## logging.error(e)
        if DEVELOPMENT:
            return jsonify({'error': e}), 400
        return jsonify({'error': "We didn't received your data in json format "}), 400

@app.route('/userAdd',methods=['POST'])
def userAdd():
    try:
        return userManagement.testFunction()
    except Exception as e:
        ## logging.error(e)
        if DEVELOPMENT:
            return jsonify({'error': e}), 400
        return jsonify({'error': "We didn't received your data in json format "}), 400


if __name__ == '__main__':
    server_port = os.environ.get('PORT', '8081')
    app.run(debug=True, port=server_port, host='0.0.0.0')

print('Completed transaction')
transactionInstance.finishTransactions()
