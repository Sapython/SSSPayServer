import json
from flask import jsonify
import requests
from core.authentication.paysprintAuth import PaySprintAuth


class HLR:
    def __init__(self, app, developmentMode):
        self.token = ''
        self.authorizedKey = ''
        self.auth = PaySprintAuth(app)
        self.developmentMode = False
        self.hlrUrl = 'https://api.paysprint.in/api/v1/service/recharge/hlrapi/hlrcheck'
        self.dthInfoUrl = 'https://api.paysprint.in/api/v1/service/recharge/hlrapi/dthinfo'
        self.browsePlanUrl = 'https://api.paysprint.in/api/v1/service/recharge/hlrapi/browseplan'
        self.utmAccountLink = "https://api.paysprint.in/api/v1/service/axisbank-utm/axisutm/generateurl"

    def getOperator(self, number: int, operatorType: str):
        payload = json.dumps({"number": number, "type": operatorType})
        print(payload)
        response = requests.request(
            "POST", self.hlrUrl, headers=self.auth.generatePaysprintAuthHeaders(), data=payload)
        print(response.json())
        if (response.json()['response_code'] == 1):
            return response.json()
        else:
            if response.json()['response_code'] != 1:
                # self.developmentMode = False
                if self.developmentMode:
                    return jsonify({
                        "status": True,
                        "response_code": 1,
                        "info": {
                            "operator": "Airtel",
                            "circle": "Delhi NCR"
                        },
                        "message": "Fetch Successful"
                    })
                else:
                    return response.json(), 400
            return {'error': 'Cannot fetch operators. Try again later'}, 400

    def getDthInfo(self, caNumber: int, operator: str):
        payload = json.dumps({"canumber": caNumber, "op": operator})
        response = requests.request(
            "POST", self.dthInfoUrl, headers=self.auth.generatePaysprintAuthHeaders(), data=payload)
        if (response.json()['response_code'] == 1):
            return response.json(), response.status_code
        else:
            if self.developmentMode:
                return response.text
            return {'error': 'Cannot fetch DTH info. Try again later'}, 400

    def getPlanInfo(self, circle: int, operator: str):
        payload = {"circle": circle, "op": operator}
        print(payload)
        response = requests.request(
            "POST", self.browsePlanUrl, headers=self.auth.generatePaysprintAuthHeaders(), json=payload)
        print(response.json())
        if (response.json()['response_code'] == 1):
            return response.json(), 200
        else:
            if self.developmentMode:
                return response.json()
            return {'error': 'Cannot fetch plan info. Try again later'}, 400

    def getUTMAccountLInk(self):
        payload = json.dumps({"merchantcode": "A002","type": 1})
        response = requests.request("POST",self.utmAccountLink , headers=self.auth.generatePaysprintAuthHeaders(), data=payload)
        return response.json()
