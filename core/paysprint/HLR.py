import json
class HLR:
    def __init__(self,app):
        self.token = ''
        self.authorizedKey = ''
        self.headers = {
            'Authorisedkey': 'MzNkYzllOGJmZGVhNWRkZTc1YTgzM2Y5ZDFlY2EyZTQ=',
            'Content-Type': 'application/json',
            'Cookie': 'ci_session=3fef906785afb3c5065ea02619e6ec6143cb3bc2'
        }
        self.hlrUrl = 'https://paysprint.in/service-api/api/v1/service/recharge/hlrapi/hlrcheck'
        self.dthInfoUrl = 'https://paysprint.in/service-api/api/v1/service/recharge/hlrapi/dthinfo'
        self.browsePlanUrl = 'https://paysprint.in/service-api/api/v1/service/recharge/hlrapi/browseplan'
    
    def getOperator(self,number:int,operatorType:str):
        payload = json.dumps({"number": number,"type": operatorType})
        response = requests.request("POST", self.hlrUrl, headers=self.headers, data=payload)
        if (response.json()['response_code']==1):
            return response.json
        else:
            return {'error': 'Cannot fetch operators. Try again later'}, 400
    
    def getDthInfo(self,caNumber:int,operator:str):
        payload = json.dumps({"canumber":caNumber,"op":operator})
        response = requests.request("POST", self.dthInfoUrl, headers=self.headers, data=payload)
        if (response.json()['response_code']==1):
            return response.json
        else:
            return {'error': 'Cannot fetch DTH info. Try again later'}, 400
    
    def getPlanInfo(self,circle:int,operator:str):
        payload = json.dumps({"circle":circle,"op":operator})
        response = requests.request("POST", self.browsePlanUrl, headers=self.headers, data=payload)
        if (response.json()['response_code']==1):
            return response.json
        else:
            return {'error': 'Cannot fetch plan info. Try again later'}, 400
    