import json
import requests
from core.authentication.paysprintAuth import PaySprintAuth
class HLR:
    def __init__(self,app):
        self.token = ''
        self.authorizedKey = ''
        self.auth = PaySprintAuth(app)
        self.hlrUrl = 'https://paysprint.in/service-api/api/v1/service/recharge/hlrapi/hlrcheck'
        self.dthInfoUrl = 'https://paysprint.in/service-api/api/v1/service/recharge/hlrapi/dthinfo'
        self.browsePlanUrl = 'https://paysprint.in/service-api/api/v1/service/recharge/hlrapi/browseplan'
    
    def getOperator(self,number:int,operatorType:str):
        payload = json.dumps({"number": number,"type": operatorType})
        response = requests.request("POST", self.hlrUrl, headers=self.auth.generatePaysprintAuthHeaders(), data=payload)
        # print(response.json())
        if (response.json()['response_code']==1):
            return response.json()
        else:
            return {'error': 'Cannot fetch operators. Try again later'}, 400
    
    def getDthInfo(self,caNumber:int,operator:str):
        payload = json.dumps({"canumber":caNumber,"op":operator})
        response = requests.request("POST", self.dthInfoUrl, headers=self.auth.generatePaysprintAuthHeaders(), data=payload)
        if (response.json()['response_code']==1):
            return response.json()
        else:
            return {'error': 'Cannot fetch DTH info. Try again later'}, 400
    
    def getPlanInfo(self,circle:int,operator:str):
        payload = json.dumps({"circle":circle,"op":operator})
        response = requests.request("POST", self.browsePlanUrl, headers=self.auth.generatePaysprintAuthHeaders(), data=payload)
        if (response.json()['response_code']==1):
            return response.json()
        else:
            return {'error': 'Cannot fetch plan info. Try again later'}, 400
    