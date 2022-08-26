import os
import jwt
import time
import base64
class PaySprintAuth:
    def __init__(self, app):
        self.app = app
        self.paySprintKey = "UFMwMDcxNmI5YWIzN2YyZDMzZWM3NDg5YjkzYzAyOGE2ZmNmZDIw"
    def generatePaysprintAuthHeaders(self):
        requestCounter = 0
        with open(os.path.join(self.app.root_path, 'database','counter.txt'),'w+') as requestCounterFile:
            if (not requestCounterFile.read()):
                requestCounter = 1
            else:
                requestCounter = int(requestCounterFile.read())
            requestCounter += 1
            requestCounterFile.seek(0)
            requestCounterFile.write(str(requestCounter))

        encodedJWT = jwt.encode({
            "timestamp":str(int(time.time())*1000),
            "partnerId":"PS00716",
            "reqid":str(requestCounter)
        }, self.paySprintKey, algorithm="HS256")
        # print(encodedJWT)
        headers = {
            'Token': encodedJWT,
            # 'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorisedkey':'ZDU2NWVlNmE3MmExMTdiYzYyOTVmMGEzN2FkNzAxZTQ='
        }
        return headers
    
    def decodeJwt(self,data):
        return jwt.decode(data,self.paySprintKey,algorithms=['HS256'])