import math
from firebase_admin import firestore
import time
import threading
from core.payment.wallet.wallet import Wallet

class CommissionAndCharges:
    def __init__(self):
        self.fs = firestore.client()
        self.commissions = []
        self.walletManager = Wallet()
        self.commission_callback_done = threading.Event()
        self.commission_col_query = self.fs.collection(u'commissions')
        self.commission_query_watch = self.commission_col_query.on_snapshot(
            self.commission_on_snapshot)
        self.charges = []
        self.charges_callback_done = threading.Event()
        self.charges_col_query = self.fs.collection(u'charges')
        self.charges_query_watch = self.charges_col_query.on_snapshot(
            self.charges_on_snapshot)

    def commission_on_snapshot(self, col_snapshot, changes, read_time):
        # print(u'Callback received query snapshot.')
        self.commissions = []
        for doc in col_snapshot:
            # print(u'Document id: {}'.format(doc.id))
            self.commissions.append(doc.to_dict())
        self.commission_callback_done.set()

    def charges_on_snapshot(self, col_snapshot, changes, read_time):
        # print(u'Callback received query snapshot.')
        self.charges = []
        for doc in col_snapshot:
            # print(u'Document id: {}'.format(doc.id))
            self.charges.append(doc.to_dict())
        self.charges_callback_done.set()

    def setCommission(self, transactionData, userId, transactionId):
        # print("Commission Data: ",transactionData)
        print("1")
        transactionData['amount'] = int(transactionData['amount'])
        access = ['admin', 'superDistributor', 'masterDistributor',
                  'distributor', 'retailer', 'guest']
        # get current user
        currentUser = self.fs.collection('users').document(userId).get().to_dict()
        users = [currentUser]
        user = currentUser.copy()
        while user.get('ownerId'):
            user = self.fs.collection('users').document(user['ownerId']).get().to_dict()
            if(user.get('ownerId') == user['userId']):
                break
            if (user.get('access').get('access') == 'admin'):
                break
            users.append(user)
        if (transactionData['serviceType'] in ['dth', 'mobile_recharge', 'aeps']):
            result = list(sorted(list(filter(
                lambda x: x['service'] == transactionData['serviceType'], self.commissions)), key=lambda y: y['minimumAmount']))
        else:
            return "No Commissions"
        print("LIST",result)
        finalRes = {}
        if not result:
            return "No Commissions"
        for res in result:
            if((res['maximumAmount'] >= int(transactionData['amount'])) and (int(transactionData['amount']) >= res['minimumAmount'])):
                finalRes = res
                break
        try:
            res = finalRes['accessLevels']
        except:
            print("No Commission charges set for price range")
            return "No Commission charges set for price range"
        charges = []
        if(finalRes):
            for accesses in finalRes['accessLevels']:
                if(finalRes['type'] == 'percentage'):
                    charges.append({
                        "access":accesses,
                        "amount":(transactionData['amount']/100)*finalRes[accesses]
                    })
                elif finalRes['type'] == 'fixed':
                    charges.append({
                        "access":accesses,
                        "amount":finalRes[accesses]
                    })
        print("8")
        commissions = []
        for member in users:
            if(member['access']['access'] in finalRes['accessLevels']):
                amount = charges[finalRes['accessLevels'].index(member['access']['access'])]['amount']
                if (amount > 0):
                    if len(list(filter(lambda x: x['member'] == member['userId'], commissions))) == 0:
                        if ((member['access']['access'] == 'retailer' and member['userId'] == userId) or member['access']['access'] != 'retailer') and member['access']['access'] in finalRes['accessLevels']:
                            commissions.append({
                                "member": member['userId'],
                                "amount": amount,
                                "name": member['displayName'],
                                "access": member['access']['access'],
                                "balance": self.walletManager.get_balance(member['userId'])
                            })
        masterCommission = 0
        for commission in commissions:
            if (commission['member'] ==currentUser['userId']):
                print("Found id",commission)
                masterCommission = commission["amount"]
        print(masterCommission)
        # deduct masterCommission from commission amount of every non matching members
        previousCommission = 0
        for commission in commissions:
            print("Commision",commission)
            val = commission["amount"]
            if (commission['member'] != currentUser['userId']):
                print("Deducting",commission["amount"],previousCommission)
                commission["amount"] = commission["amount"] - previousCommission
            previousCommission = val
        print("9")
        self.fs.collection('users').document(userId).collection('transaction').document(transactionId).update({
            "commissions": firestore.ArrayUnion(commissions)
        })
        for commission in commissions:
            narration = "Commission added in wallet from "+userId
            print(narration,amount,commission['amount'])
            self.walletManager.add_balance(commission['member'],commission['amount'],narration,transactionData['serviceType'],'Commission')
            self.fs.collection('users').document(commission['member']).update({"totalCommission": firestore.Increment(commission['amount'])})
            self.fs.collection('users').document(commission['member']).collection('commissions').add({
                **transactionData,
                'exchangeAmount': commission['amount'],
                'member': commission['member'],
                "name": commission['name'],
                "ownerId": userId,
                'transactionType': 'debit',
                'transactionTime': firestore.SERVER_TIMESTAMP
            })
        return {"commissions": commissions,"type":finalRes}, 200

    def getAmount(self, transactionData, userId):
        print("self.charges",self.charges)
        result = list(sorted(list(filter(
            lambda x: x['service'] == transactionData['serviceType'], self.charges)), key=lambda y: y['minimumAmount']))
        print("Charge", result)
        finalRes = {}
        user = self.fs.collection('users').document(userId).get().to_dict()
        for res in result:
            print("COND", res['maximumAmount'], transactionData['amount'], res['minimumAmount'], (
                res['maximumAmount'] >= transactionData['amount']), (transactionData['amount'] >= res['minimumAmount']))
            if((res['maximumAmount'] >= transactionData['amount']) and (transactionData['amount'] >= res['minimumAmount'])):
                finalRes = res[user['access']['access']]
                break
        if (finalRes == {}):
            finalRes = 0
        return finalRes
