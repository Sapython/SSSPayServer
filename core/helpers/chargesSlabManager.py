from firebase_admin import firestore
class ChargesSlabManager:
    def __init__(self,developmentMode):
        self.developmentMode = developmentMode
        self.fs = firestore.client()

    def getCommission(self,paymentType,amount):
        docs = self.fs.collection('commissions').where(u'minimumAmount','>=',str(amount)).where(u'maximumAmount','>',str(amount)).where(u'service','==',str(paymentType)).stream()
        for doc in docs:
            return doc.to_dict()
        else:
            return []
    
    def getChargesSlab(self,paymentType,amount):
        docs = self.fs.collection('chargesSlab').where(u'minimumAmount','>=',str(amount)).where(u'maximumAmount','>',str(amount)).where(u'service','==',str(paymentType)).stream()
        for doc in docs:
            return doc.to_dict()
        else:
            return []