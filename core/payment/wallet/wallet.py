from firebase_admin import firestore
class Wallet:
    def __init__(self):
        self.firestore = firestore.client()

    def get_balance(self,userId):
        balanceData = self.firestore.collection('users').document(userId).collection('wallet').document('wallet').get()
        print("Balance data: ",balanceData)
        if balanceData.exists:
            return balanceData.to_dict()['balance']
        else:
            return -1

    def add_balance(self,userId, amount,narration,service):
        updateWrite = self.firestore.collection('users').document(userId).collection('wallet').document('wallet').update({"balance": firestore.Increment(amount)})
        self.firestore.collection('users').document(userId).collection('walletNarration').add({
            "amount": amount,
            "narration": narration,
            "service":service,
            "transactionType":"credit",
            "transactionTime":firestore.SERVER_TIMESTAMP
        })
        print("CREDIT: Update write: ",updateWrite)
        if updateWrite:
            return {"message":"Updated successfully"}
        else:
            return -1
        

    def deduct_balance(self,userId, amount,narration,service):
        updateWrite = self.firestore.collection('users').document(userId).collection('wallet').document('wallet').update({"balance": firestore.Increment(-amount)})
        self.firestore.collection('users').document(userId).collection('walletNarration').add({
            "amount": amount,
            "narration": narration,
            "service":service,
            "transactionType":"debit",
            "transactionTime":firestore.SERVER_TIMESTAMP
        })
        print("DEBIT: Update write: ",updateWrite)
        if updateWrite:
            return {"message":"Updated successfully"}
        else:
            return -1
        