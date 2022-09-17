import os
import jwt
import time
import base64
class PaySprintAuth:
    def __init__(self, app):
        self.app = app
        self.paySprintKey = "UFMwMDE2MTk1NjNkNThkNjM1NDAyYjRkMjg3M2Q3MmRjNDAyYjAwYg=="
    def generatePaysprintAuthHeaders(self):
        # Generate random number using time the timestamp
        requestCounter = str(int(time.time()))
        encodedJWT = jwt.encode({
            "timestamp":str(int(time.time())*1000),
            "partnerId":"PS001619",
            "reqid":str(requestCounter)
        }, self.paySprintKey, algorithm="HS256")
        # print(encodedJWT)
        headers = {
            'Token': encodedJWT,
            # 'Content-Type': 'application/json',
            'Accept': 'application/json',
            # 'Authorisedkey':'ZDU2NWVlNmE3MmExMTdiYzYyOTVmMGEzN2FkNzAxZTQ='
        }
        return headers
    
    def decodeJwt(self,data):
        return jwt.decode(data,self.paySprintKey,algorithms=['HS256'])