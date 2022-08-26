from core.messaging.messaging import Messaging
from firebase_admin import firestore

class Notification:
    def __init__(self, developmentMode):
        self.developmentMode = developmentMode
        self.messaging = Messaging()
        self.firestore = firestore.client()
    
    def send(self, message,phoneNumber = 0,userId="",notificationType="",priority="ndnd"):
        if (phoneNumber):
            self.messaging.sendSingleSMS(message,phoneNumber,priority)
        if (userId):
            self.firestore.collection('users').document(userId).collection('notifications').add({
                    "message": message,
                    "phoneNumber": phoneNumber,
                    "type": notificationType,
                    "priority": priority,
                    "time": firestore.SERVER_TIMESTAMP
                })