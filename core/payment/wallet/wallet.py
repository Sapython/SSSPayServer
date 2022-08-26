import json
import base64
import requests
import datetime
from firebase_admin import firestore
from core.authentication.encryption import Encrypt
from core.authentication.paysprintAuth import PaySprintAuth
class Wallet:
    def __init__(self, app):
        self.app = app
        self.firestore = firestore.client()

    def get_balance(self,userId):
        balanceData = self.firestore.collection('users').document(userId).collection('wallet').document('wallet').get()
        if balanceData.exists:
            return balanceData.to_dict()['balance']
        else:
            return -1

    def add_balance(self,userId, amount):
        updateWrite = self.firestore.collection('users').document(userId).collection('wallet').document('wallet').update({"balance": firestore.Increment(amount)})
        if updateWrite:
            return {"message":"Updated successfully"}
        else:
            return -1
        pass

    def deduct_balance(self,userId, amount):
        updateWrite = self.firestore.collection('users').document(userId).collection('wallet').document('wallet').update({"balance": firestore.Increment(-amount)})
        if updateWrite:
            return {"message":"Updated successfully"}
        else:
            return -1
        pass