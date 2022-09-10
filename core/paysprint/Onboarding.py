import json
import base64
from subprocess import call
import requests
import datetime
from firebase_admin import firestore
from core.authentication.encryption import Encrypt
from core.authentication.paysprintAuth import PaySprintAuth

class Onboarding:
    def __init__(self, app,logging):
        self.auth = PaySprintAuth(app)
        self.logging = logging
        self.encrypt = Encrypt()
        self.fs = firestore.client()

    def onboardingWeb(self,merchantCode:str,mobile:int,is_new:int,email:str,referenceId:str):
        url = "https://paysprint.in/service-api/api/v1/service/onboard/onboardnew/getonboardurl"
        merchantCode = {
            "merchantcode": merchantCode,
            "mobile": str(mobile),
            "is_new": str(is_new),
            "email": email,
            "firm": "SSSPay",
            "callback": f"https://ssspay-proxy-server-76zqkqboia-em.a.run.app/onboarding/callback"
        }
        response = requests.post(url, json=merchantCode,headers=self.auth.generatePaysprintAuthHeaders())
        print(response.content == response.text)
        print(response.content == response.json())
        print(response.text)
        return response.json()
    
    def checkStatus(self,data):
        # print("-----------")
        # print("STATUS ",data)
        # print("-----------")
        url = "https://paysprint.in/service-api/api/v1/service/onboard/onboard/getonboardstatus"
        if not data['mobile']:
            return {"status":400,"message":"Mobile number is required"}, 400
        if not data['merchantcode']:
            return {"status":400,"message":"Merchant code is required"}, 400
        data['pipe'] = 'bank1'
        response = requests.post(url, json=data,headers=self.auth.generatePaysprintAuthHeaders())
        return response.json(), response.status_code


    def handleCallbackData(self,data):
        callback = self.encrypt.decrypt(data)
        if (callback['refno']):
            user = self.fs.collection('users').document(callback['refno']).get()
            userData = user.to_dict()
            if (user.exists):
                if (userData['kycStatus']!='rejected'):
                    if (userData['status']['access']=='active' or userData['status']['access']=='inactive'):
                        if (userData['access']['access']!='guest'):
                            return {"status":200,"message":"Transaction completed successfully"}, 200
                        else:
                            return {"status":400,"message":"Transaction failed because access not allowed"}, 200
                    else:
                        return {"status":400,"message":"Transaction failed because user is deactivated or deleted"}, 200
                else:
                    return {"status":400,"message":"Transaction failed because user is rejected for internal kyc"}, 200
            else:
                return {"status":400,"message":"Transaction failed because user not found"}, 200
    

    
            
