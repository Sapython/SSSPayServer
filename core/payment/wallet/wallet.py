from firebase_admin import firestore
class Wallet:
    def __init__(self):
        self.firestore = firestore.client()

    def get_balance(self,userId):
        balanceData = self.firestore.collection('users').document(userId).collection('wallet').document('wallet').get()
        if (balanceData.to_dict() == None):
            self.firestore.collection('users').document(userId).collection('wallet').document('wallet').set({"balance":0})
            return 0
        print("Balance data: ",balanceData,balanceData.to_dict())
        if balanceData.exists:
            return balanceData.to_dict()['balance']
        else:
            return -1

    def add_balance(self,userId, amount,narration,service,actionType):
        print("Increasing Amount: ",amount)
        updateWrite = self.firestore.collection('users').document(userId).collection('wallet').document('wallet').update({"balance": firestore.Increment(int(amount))})
        print("Amount increased")
        self.firestore.collection('users').document(userId).collection('walletNarration').add({
            "amount": amount,
            "narration": narration,
            "service":service,
            "balance":self.get_balance(userId),
            "transactionType":"credit",
            "transactionTime":firestore.SERVER_TIMESTAMP,
            "actionType":actionType,
        })
        print("Narration added")
        

    def deduct_balance(self,userId, amount,narration,service,actionType):
        updateWrite = self.firestore.collection('users').document(userId).collection('wallet').document('wallet').update({"balance": firestore.Increment(-amount)})
        self.firestore.collection('users').document(userId).collection('walletNarration').add({
            "amount": amount,
            "narration": narration,
            "service":service,
            "balance":self.get_balance(userId),
            "transactionType":"debit",
            "transactionTime":firestore.SERVER_TIMESTAMP,
            "actionType":actionType
        })
        print("DEBIT: Update write: ",updateWrite)
        if updateWrite:
            return {"message":"Updated successfully"}
        else:
            return -1
        