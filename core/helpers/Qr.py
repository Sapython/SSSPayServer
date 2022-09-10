import requests
from firebase_admin import firestore
from core.messaging.notification import Notification


class QR:
    def __init__(self, development):
        self.development = development
        self.secretKey = '7od0YTzDp656LZT1qcNop4Nc'
        self.keyId = 'rzp_test_iXjGFXuZaNQ1Uk'
        self.fs = firestore.client()

    def generateQr(self, storeName, userId):
        payload = {
            "type": "upi_qr",
            "name": storeName,
            "usage": "multiple_use",
            "fixed_amount": False,
            "description": "SSSPay QR payment",
            "notes": {
                "userId": userId
            }
        }
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.post('https://api.razorpay.com/v1/payments/qr_codes',
                      json=payload, headers=headers, auth=(self.keyId, self.secretKey))
        print(response.text,response.json())
        if (response.json()['error']):
            return response.json(),400
        else:
            self.fs.collection('users').document(userId).collection('qr').document('qr').update({
                'qrCode': response.json()
            })
            return response.json(),200
        
