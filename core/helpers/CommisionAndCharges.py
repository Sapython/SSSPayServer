import math
from firebase_admin import firestore
import time
import threading
class CommissionAndCharges:
    def __init__(self):
        self.fs = firestore.client()
        self.commissions = []
        self.commission_callback_done = threading.Event()
        self.commission_col_query = self.fs.collection(u'commissions')
        self.commission_query_watch = self.commission_col_query.on_snapshot(self.commission_on_snapshot)
        self.charges = []
        self.charges_callback_done = threading.Event()
        self.charges_col_query = self.fs.collection(u'charges')
        self.charges_query_watch = self.charges_col_query.on_snapshot(self.charges_on_snapshot)

    def commission_on_snapshot(self,col_snapshot, changes, read_time):
        print(u'Callback received query snapshot.')
        self.commissions = []
        for doc in col_snapshot:
            print(u'Document id: {}'.format(doc.id))
            self.commissions.append(doc.to_dict())
        self.commission_callback_done.set()

    def charges_on_snapshot(self,col_snapshot, changes, read_time):
        print(u'Callback received query snapshot.')
        self.charges = []
        for doc in col_snapshot:
            print(u'Document id: {}'.format(doc.id))
            self.charges.append(doc.to_dict())
        self.charges_callback_done.set()
        
    def setCommission(self,transactionData,userId,transactionId):
        print("Commission Data: ",transactionData)
        members = self.fs.collection('groups').document(transactionData['groupId']).get()
        # print(self.commissions)
        isCommission = False
        if (transactionData['serviceType'] in ['dth','mobile_recharge','aeps']):
            result = list(sorted(list(filter(lambda x: x['service'] == transactionData['serviceType'], self.commissions)),key=lambda y:y['minimumAmount']))
            print("Commission",result)
            isCommission = True
        if (not isCommission):
            return
        elif (transactionData['serviceType'] in ['expressPayoutUpi','expressPayoutImps','payoutImps','payoutUPI']):
            result = list(sorted(list(filter(lambda x: x['service'] == transactionData['serviceType'], self.charges)),key=lambda y:y['minimumAmount']))
            print("Charge",result)
        else:
            print("No Commission")
            return "No ADDITIONAL FOUND"
        finalRes = {}
        # print("result",result)
        # transactionData = self.fs.collection('users').document(userId).collection('transaction').document(transactionID).get().to_dict()
        for res in result:
            print("COND",res['maximumAmount'],transactionData['amount'],res['minimumAmount'],(res['maximumAmount'] >= transactionData['amount']),( transactionData['amount'] >= res['minimumAmount']))
            if((res['maximumAmount'] >= transactionData['amount']) and ( transactionData['amount'] >= res['minimumAmount'])):
                finalRes = res
                break
        try:
            res = finalRes['accessLevels']
        except:
            print("No Commission charges set for price range")
            return "No Commission charges set for price range"
        charges = []
        print("finalRes",finalRes)
        if(finalRes):
            for accesses in finalRes['accessLevels']:
                if(finalRes['type']=='percentage'):
                    charges.append((finalRes[accesses]/100)*transactionData['amount'])
                elif finalRes['type']=='fixed':
                    charges.append(finalRes[accesses])
        totalCharge = 0
        for member in members.to_dict()['members']:
            print("Member",member)
            if(member['access']['access'] in finalRes['accessLevels']):
                # print()
                amount = math.floor(charges[finalRes['accessLevels'].index(member['access']['access'])])
                if (not isCommission):
                    amount = -amount
                print(amount)
                totalCharge += amount
                self.fs.collection('users').document(userId).collection('wallet').document('wallet').update({
                    'balance': firestore.Increment(amount)
                })
                transactionType = 'credit'
                if (not isCommission):
                    transactionType = 'debit'
                self.fs.collection('groups').document(transactionData['groupId']).collection('transactions').add({
                    **transactionData,
                    'exchangeAmount': amount,
                    'member': member['id'],
                    "ownerId": userId,
                    'transactionType': transactionType,
                    'transactionTime': firestore.SERVER_TIMESTAMP
                })
        
        self.fs.collection('users').document(userId).collection('transaction').document(transactionId).update({
            "additionalAmount": totalCharge
        })

    def getAmount(self,transactionData,userId):
        result = list(sorted(list(filter(lambda x: x['service'] == transactionData['serviceType'], self.charges)),key=lambda y:y['minimumAmount']))
        print("Charge",result)
        finalRes = {}
        user = self.fs.collection('users').document(userId).get().to_dict()
        for res in result:
            print("COND",res['maximumAmount'],transactionData['amount'],res['minimumAmount'],(res['maximumAmount'] >= transactionData['amount']),( transactionData['amount'] >= res['minimumAmount']))
            if((res['maximumAmount'] >= transactionData['amount']) and ( transactionData['amount'] >= res['minimumAmount'])):
                finalRes = res[user['access']['access']]
                break
        return finalRes
