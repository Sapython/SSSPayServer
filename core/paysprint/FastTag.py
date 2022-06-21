import json
class FasTag:
    def __init__(self,app):
        self.header = {
            'Authorisedkey': 'MzNkYzllOGJmZGVhNWRkZTc1YTgzM2Y5ZDFlY2EyZTQ=',
            'Content-Type': 'application/json',
            'Cookie': 'ci_session=3fef906785afb3c5065ea02619e6ec6143cb3bc2'
        }
        self.operatorListUrl = 'https://paysprint.in/service-api/api/v1/service/fastag/Fastag/operatorsList'
        self.fetchConsumerDetailsUrl = 'https://paysprint.in/service-api/api/v1/service/fastag/Fastag/fetchConsumerDetails'
        self.rechargeUrl = 'https://paysprint.in/service-api/api/v1/service/fastag/Fastag/recharge'
        self.getStatusURl = 'https://paysprint.in/service-api/api/v1/service/fastag/Fastag/status'

    def getOperatorsList(self):
        response = requests.request(
            "POST", self.operatorListUrl, headers=self.header)
        if (response.json()['response_code'] == 1):
            return response.json
        else:
            return {'error': 'Cannot fetch operators. Try again later'}, 400

    def fetchConsumerDetails(self, operator: int, caNumber: str):
        payload = json.dumps({
            "operator": operator,
            "canumber": caNumber
        })
        response = requests.request(
            "POST", self.fetchConsumerDetailsUrl, headers=self.header, data=payload)
        if (response.json()['response_code'] == 1):
            return response.json
        else:
            return {'error': response.json()['message']}, 400

    def recharge(self, operator: int, caNumber: str, amount: int, referenceId: str, latitude: str, longitude: str,billAmount:str,billNetAmount:str,dueDate:str,maxBillAmount:str,acceptPayment:bool,acceptPartPay:bool,cellNumber:str,userName:str):
        payload = json.dumps({"operator": operator, "canumber": caNumber, "amount": amount, "referenceid": referenceId, "latitude": latitude, "longitude": longitude, "bill_fetch": {"billAmount": billAmount,     "billnetamount": billNetAmount,
                             "dueDate": dueDate,     "maxBillAmount": maxBillAmount,     "acceptPayment": acceptPayment,     "acceptPartPay": acceptPartPay,     "cellNumber": cellNumber,     "userName": userName}})
        response = requests.request(
            "POST", self.rechargeUrl, headers=self.header, data=payload)
        if (response.json()['response_code'] == 1):
            return response.json
        else:
            return {'error': response.json()['message']}, 400
    
    def getFastTagStatus(self,referenceId:str):
        payload = json.dumps({"referenceId": referenceId})
        response = requests.request(
            "POST", self.getStatusURl, headers=self.header, data=payload)
        if (response.json()['response_code'] == 1):
            return response.json
        else:
            return {'error': response.json()['message']}, 400
