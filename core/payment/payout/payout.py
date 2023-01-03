import json
import requests
import datetime
from firebase_admin import firestore
from core.authentication.encryption import Encrypt
from core.helpers.CommisionAndCharges import CommissionAndCharges
from firebase_admin import firestore


class Payout:
    def __init__(self, app):
        # self.secretKey = '7od0YTzDp656LZT1qcNop4Nc'
        # self.keyId = 'rzp_test_iXjGFXuZaNQ1Uk'
        self.keyId = 'rzp_live_tlXdDUmbEQxwf9'
        self.secretKey = '0bbPbrfVDHYc7gJNgCCbBxdr'
        self.fs = firestore.client()
        self.commisionManager = CommissionAndCharges()
        self.accountNumberVpa = ""
        self.accountNumberBank = ""
        self.app = app
        self.createAccountURL = "https://api.razorpay.com/v1/contacts"
        self.fundAccountTypes = ['bank_account', 'vpa', 'card']
        self.DEVELOPMENT = False
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Basic Og=='
        }

    def createAccount(self, requestData):
        userId = requestData['uid']
        payload = json.dumps({
            "name": requestData['name'],
            "email": requestData['email'],
            "contact": requestData['contact'],
            "type": "employee",
            "notes": {
                "userId": userId
            }
        })
        response = requests.request("POST", self.createAccountURL, auth=(
            self.keyId, self.secretKey), headers=self.headers, data=payload)
        print(response.text, response.status_code)
        return response.json(), response.status_code

    def getAllAccounts(self):
        url = "https://api.razorpay.com/v1/contacts"
        payload = ""
        response = requests.request("GET", url, auth=(
            self.keyId, self.secretKey), headers=self.headers, data=payload)
        print(response.text, response.status_code)
        return response.json(), response.status_code

    def getAccount(self, accountId):
        url = f"https://api.razorpay.com/v1/contacts/{accountId}"
        payload = {}
        headers = {
            'Authorization': 'Basic Og=='
        }
        response = requests.request("GET", url, auth=(
            self.keyId, self.secretKey), headers=headers, data=payload)
        print(response.text, response.status_code)
        return response.json(), response.status_code

    def updateAccount(self, requestData):
        url = f"https://api.razorpay.com/v1/contacts/{requestData['accountId']}"
        payload = json.dumps({
            "name": requestData['name'],
            "email": requestData['email'],
            "contact": requestData['contact'],
            "type": "vendor",
            "notes": {
                "userId": requestData['uid'],
            }
        })
        response = requests.request("PATCH", url, auth=(
            self.keyId, self.secretKey), headers=self.headers, data=payload)
        print(response.text, response.status_code)
        return response.json(), response.status_code

    def activateAccount(self, accountId):
        url = f"https://api.razorpay.com/v1/contacts/{accountId}"
        payload = json.dumps({
            "active": True
        })
        response = requests.request("PATCH", url, auth=(
            self.keyId, self.secretKey), headers=self.headers, data=payload)
        print(response.text, response.status_code)
        return response.json(), response.status_code

    def deactivateAccount(self, accountId):
        url = f"https://api.razorpay.com/v1/contacts/{accountId}"
        payload = json.dumps({
            "active": False
        })
        response = requests.request("PATCH", url, auth=(
            self.keyId, self.secretKey), headers=self.headers, data=payload)
        print(response.text, response.status_code)
        return response.json(), response.status_code

    def connectFundAccount(self, requestData):
        url = "https://api.razorpay.com/v1/fund_accounts"
        if (requestData['account_type'] in self.fundAccountTypes):
            if requestData['account_type'] == self.fundAccountTypes[0]:
                payload = json.dumps({
                    "contact_id": requestData['accountId'],
                    "account_type": "bank_account",
                    "bank_account": {
                        "name": requestData['bankAccountName'],
                        "ifsc": requestData['ifsc'],
                        "account_number": requestData['accountNumber'],
                    }
                })
            elif requestData['account_type'] == self.fundAccountTypes[1]:
                payload = json.dumps({
                    "contact_id": requestData['accountId'],
                    "account_type": requestData['account_type'],
                    "vpa": {
                        "address":requestData['vpa']
                    }
                })
            elif requestData['account_type'] == self.fundAccountTypes[2]:
                payload = json.dumps({
                    "contact_id": requestData['accountId'],
                    "account_type": "card",
                    "card": {
                        "name": requestData['cardName'],
                        "number": requestData['cardNumber'],
                    }
                })
            else:
                raise Exception("Invalid account type")
                return None, None, None
        response = requests.request("POST", url, auth=(
            self.keyId, self.secretKey), headers=self.headers, data=payload)
        print(response.text, response.status_code)
        return response.json(), response.status_code

    def getAllFundAccounts(self):
        url = "https://api.razorpay.com/v1/fund_accounts"
        payload = {}
        response = requests.request(
            "GET", url, auth=(
            self.keyId, self.secretKey), headers=self.headers, data=payload)
        print(response.text, response.status_code)
        return response.json(), response.status_code

    def getFundAccountById(self,fa_id):
        url = "https://api.razorpay.com/v1/fund_accounts/{fa_id}"
        payload = {}
        response = requests.request(
            "GET", url, auth=(
            self.keyId, self.secretKey), headers=self.headers, data=payload)
        print(response.text, response.status_code)
        return response.json(), response.status_code

    def createPayout(self, requestData, purpose):
        url = "https://api.razorpay.com/v1/payouts"
        if requestData['mode'] == 'card':
            payload = json.dumps({
                "account_number": requestData['account_number'],
                "fund_account_id": requestData['fund_account_id'],
                "amount": requestData['amount'],
                "currency": "INR",
                "mode": requestData['mode'],
                "purpose": purpose,
                "queue_if_low_balance": True,
                "reference_id": requestData['referenceId'],
                "narration": requestData['narration'],
                "notes": {
                    "userId": requestData['uid']
                }
            })
        response = requests.request(
            "POST", url, auth=(
            self.keyId, self.secretKey), headers=self.headers, data=payload)
        print(response.text, response.status_code)
        return response.json(), response.status_code

    def getAllPayouts(self,account_number):
        url = "https://api.razorpay.com/v1/payouts?account_number={account_number}"
        payload = ""
        response = requests.request(
            "GET", url, auth=(
            self.keyId, self.secretKey), headers=self.headers, data=payload)
        print(response.text, response.status_code)
        return response.json(), response.status_code

    def getPayoutById(self, payoutId):
        url = "https://api.razorpay.com/v1/payouts/{payoutId}"
        payload = ""
        response = requests.request(
            "GET", url, auth=(
            self.keyId, self.secretKey), headers=self.headers, data=payload)
        print(response.text, response.status_code)
        return response.json(), response.status_code

    def cancelQueuedPayout(self,pout_id):
        url = "https://api.razorpay.com/v1/payouts/{pout_id}/cancel"
        payload = {}
        response = requests.request(
            "POST", url, auth=(
            self.keyId, self.secretKey), headers=self.headers, data=payload)
        print(response.text, response.status_code)
        return response.json(), response.status_code

    def verifyUpi(self,upiId):
        url = "https://api.razorpay.com/v1/payments/validate/vpa"
        payload = json.dumps({
            "vpa": upiId
        })
        response = requests.request(
            "POST", url, auth=(
            self.keyId, self.secretKey), headers=self.headers, data=payload)
        print(response.text, response.status_code)
        return response.json(), response.status_code

    def quickPayout(self, requestData, payoutType, Idempotency):
        print(requestData)
        url = f"https://api.razorpay.com/v1/payouts"
        charge = self.commisionManager.getAmount(requestData,requestData['uid'])
        print("TOTAL CHARGE",charge)
        self.fs.collection('users').document(requestData['uid']).collection('transaction').document(requestData['referenceId']).update({
            "additionalAmount":-charge
        })
        self.fs.collection('users').document(requestData['uid']).collection('wallet').document('wallet').update({
            'balance': firestore.Increment(-charge)
        })
        requestData['amount'] = requestData['amount'] - charge
        if (requestData['amount'] <= 0):
            return {"error":"Not enough balance.","message":"Not enough balance."}, 400
        if (payoutType == 'bank_account'):
            fundAccountData = {
                "account_type": "bank_account",
                "bank_account": {
                    "name": requestData['extraData']['account']['bankAccountName'],
                    "ifsc": requestData['extraData']['account']['ifsc'],
                    "account_number": requestData['extraData']['account']['accountNumber'],
                },
                "contact": {
                    "name": requestData['extraData']['account']['name'],
                    "email": requestData['extraData']['account']['email'],
                    "contact": requestData['extraData']['account']['contact'],
                    "type": "vendor",
                    "notes": {
                        "payoutType": payoutType,
                        "customerId": requestData['extraData']['customerId']
                    }
                }
            }
        elif (payoutType == 'vpa'):
            fundAccountData = {
                "account_type": "vpa",
                "vpa": {
                    "address": requestData['extraData']['account']['vpa']
                },
                "contact": {
                    "name": requestData['extraData']['account']['name'],
                    "email": requestData['extraData']['account']['email'],
                    "contact": requestData['extraData']['account']['contact'],
                    "type": "vendor",
                    "notes": {
                        "payoutType": payoutType,
                        "customerId": requestData['extraData']['customerId']
                    }
                }
            }
        elif (payoutType == 'card'):
            fundAccountData = {
                "account_type": "card",
                "card": {
                    "number": requestData['extraData']['account']['cardNumber'],
                    "name": requestData['extraData']['account']['cardName'],
                },
                "contact": {
                    "name": requestData['extraData']['account']['name'],
                    "email": requestData['extraData']['account']['email'],
                    "contact": requestData['extraData']['account']['contact'],
                    "type": "vendor",
                    "notes": {
                        "payoutType": payoutType,
                        "customerId": requestData['extraData']['customerId']
                    }
                }
            }
        else:
            raise Exception("Invalid payout type")
        if requestData['extraData']['accountType'] == 'bank_account':
            # accountNumber = "000405657647"
            accountNumber = "4564563801628609"
        elif requestData['extraData']['accountType'] == 'vpa':
            accountNumber = "4564563801628609"
        else:
            return {"error":"Wrong account type"}, 400
        print("customerId",requestData['extraData']['customerId'])
        print("paymentType",requestData['extraData']['paymentType'])
        if (requestData['extraData']['paymentType'] == None):
            requestData['extraData']['paymentType'] = "IMPS"
        print("Account number",accountNumber)
        print('PaymentType',requestData['extraData']['paymentType'])
        if self.DEVELOPMENT:
            accountNumber = "2323230045367581"
        payload = json.dumps({
            "account_number": accountNumber,
            "amount": requestData['amount']*100,
            "currency": "INR",
            "mode": requestData['extraData']['paymentType'],
            "purpose": "payout",
            "fund_account": fundAccountData,
            "queue_if_low_balance": True,
            "reference_id": requestData['referenceId'],
            "narration": "SSSPay Express payout transfer",
            "notes": {
                "userId": requestData['uid'],
                "payoutType": payoutType,
                "customerId": requestData['extraData']['customerId'],
                "serviceType":requestData['serviceType'],
                "dailyPayoutTime":requestData['extraData']['dailyPayoutTime'],
            }
        })
        print('-'*20)
        print('PAYLOAD',payload)
        print('-'*20)
        response = requests.request("POST", url, auth=(
            self.keyId, self.secretKey), headers=self.headers, data=payload)
        print("response.text",response.text,"response.status",response.status_code)
        return response.json(), response.status_code
