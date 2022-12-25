from datetime import datetime, tzinfo
from firebase_admin import firestore
from threading import Thread
from core.messaging.notification import Notification
import time
import pytz
utc = pytz.UTC
from dateutil import parser

class Transaction:
    def __init__(self, app, DEVELOPMENT):
        self.app = app
        self.DEVELOPMENT = DEVELOPMENT
        self.fs = firestore.client()
        self.processes = []
        self.notification = Notification(DEVELOPMENT)
        # self.completeTransactionProcessThread = Process(target=self.completeTransactionProcess)

    def getTransaction(self, userId: str, transactionId: str):
        return self.fs.collection('users').document(userId).collection('transaction').document(transactionId).get().to_dict()

    def pendingTransaction(self, userId: str, transactionId: str, message: str, paymentType: str, successData: dict):
        process = Thread(target=self.pendingTransactionProcess, args=(
            userId, transactionId, message, paymentType, successData))
        self.processes.append(process)
        process.start()

    def completeTransaction(self, userId: str, transactionId: str, message: str, paymentType: str, successData: dict):
        process = Thread(target=self.completeTransactionProcess, args=(
            userId, transactionId, message, paymentType, successData))
        self.processes.append(process)
        process.start()

    def failedTransaction(self, userId: str, transactionId: str, successData: dict):
        process = Thread(target=self.failedTransactionProcess, args=(
            userId, transactionId, successData))
        self.processes.append(process)
        process.start()

    def failedTransactionProcess(self, userId: str, transactionId: str, errorData: dict):
        startTime = time.time()
        userData = self.fs.collection('users').document(userId).get().to_dict()
        print(userData)
        if (userData):
            # self.notification.send(
            #     message, userData['phoneNumber'], userData['uid'], paymentType)
            self.fs.collection(
                'users').document(userId).collection(
                    'transaction').document(transactionId).update(
                {
                    "completed": False,
                    "status": "error",
                    "error": errorData
                })
            print('Transaction completed', time.time() - startTime)

    def pendingTransactionProcess(self, userId: str, transactionId: str, message: str, paymentType: str, successData: dict):
        startTime = time.time()
        userData = self.fs.collection('users').document(userId).get().to_dict()
        print("userId", userId, "userData", userData)
        # self.notification.send(
        #     message, userData['phoneNumber'], userData['userId'], paymentType)
        self.fs.collection(
            'users').document(userId).collection(
                'transaction').document(transactionId).update(
            {
                "completed": False,
                "status": "pending",
                "successData": successData
            })
        print('Transaction completed', time.time() - startTime)

    def completeTransactionProcess(self, userId: str, transactionId: str, message: str, paymentType: str, successData: dict):
        startTime = time.time()
        userData = self.fs.collection('users').document(userId).get().to_dict()
        if (userData):
            print(userData)
            # self.notification.send(
            #     message, userData['phoneNumber'], userData['userId'], paymentType)
            self.fs.collection(
                'users').document(userId).collection(
                    'transaction').document(transactionId).update(
                {
                    "completed": True,
                    "status": "success",
                    "successData": successData
                })
            print('Transaction completed', time.time() - startTime)

    def checkBalance(self, amount: int, userId: str):
        user = self.fs.collection('users').document(
            userId).collection('wallet').document('wallet').get()
        if user.exists:
            data = user.to_dict()
            print("WALLET", data)
            if data['balance'] >= amount:
                return True
            else:
                return False
        else:
            return False

    def finishTransactions(self):
        for process in self.processes:
            process.join()

    def getTransactions(self, transactionType: str, startDate: str, endDate: str):
        if not transactionType:
            raise Exception("Type is required")
        users = self.fs.collection('users').stream()
        transactions = []
        # data = self.fs.collection('users').document('bwYXqVOM8YdxzDk9ltxY7TAiBId2').collection(
        #     'transaction').document('EmBnGDQ2BUvmj9kmftSk').get()
        # print(data.to_dict())
        # print(data.to_dict()['date'], parser.parse(startDate))
        # print(data.to_dict()['date'] < parser.parse(startDate))
        # return {"status":data.to_dict()['date'] < parser.parse(startDate)},200
        for user in users:
            userTransactions = self.fs.collection('users').document(user.id).collection('transaction').stream()
            for transaction in userTransactions:
                if startDate and endDate:
                    if transaction.to_dict()['date'] >= parser.parse(startDate) and transaction.to_dict()['date'] < parser.parse(endDate) and transaction.to_dict()['type'] == transactionType:
                        transactions.append(transaction.to_dict())
                    else:
                        continue
                elif transaction.to_dict()['type'] == transactionType:
                    # if transactionType=='bbps':
                    #     data = {
                    #         transaction.to_dict()
                    #     }
                    #     transactions.append()
                    transactions.append(transaction.to_dict())
        return {"transactions":transactions,"response_code":1},200
    
    def getUser(self,userId):
        return self.fs.collection('users').document(userId).get().to_dict()

    
