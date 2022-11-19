import hashlib
import os
import jwt
import time
import random
class PaySprintAuth:
    def __init__(self, app):
        self.app = app
        self.paySprintKey = "UFMwMDE2MTk1NjNkNThkNjM1NDAyYjRkMjg3M2Q3MmRjNDAyYjAwYg=="
    def generatePaysprintAuthHeaders(self):
        # Generate random number of 15 length
        requestCounter = random.randint(100000000000000,999999999999999)
        timestamp = str(int(time.time()))
        print("TIMESTAMP",timestamp)
        encodedJWT = jwt.encode({
            "timestamp":timestamp,
            "partnerId":"PS001619",
            "reqid":str(requestCounter)
        }, self.paySprintKey, algorithm="HS256")
        # print(encodedJWT)
        # encodedJWT = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0aW1lc3RhbXAiOjE2NjQwMjU0MTgsInBhcnRuZXJJZCI6IlBTMDAxNjE5IiwicmVxaWQiOiJFV0czNDUyNTEyMzQifQ.Qu4ZKNL6aj22iE0vmensnoWnoslRBCep910xT7fSRKQ"
        headers = {
            'Token': encodedJWT,
            # 'Content-Type': 'application/json',
            'Accept': 'application/json',
            # 'Authorisedkey':'ZDU2NWVlNmE3MmExMTdiYzYyOTVmMGEzN2FkNzAxZTQ='
        }
        return headers
    
    def generateFiddpayAuthHeaders():
        timestamp = str(int(time.time()))
        data = {
            "trnTimestamp":timestamp,
            "hash":""
        }
        encryptionData = {
            "username":"",
            "password":"password",
            "timestamp":21312,
            "latitude":1,
            "longitude":2,
            "supermerchantId":'',
            "merchants":[{
                "merchantLoginId":"",
                "merchantLoginPin":"",
                "merchantName":"",
                "merchantAddress":{
                    "merchantAddress":"",
                    "merchantState":""
                },
                "merchantPhoneNumber":43298479823,
                "companyLegalName":"dsjhfk",
                "companyMarketingName":"",
                "kyc":{
                    "userPan":"fdsfsd",
                    "aadhaarNumber":"4322342342",
                    "gstInNumber":"483274987234",
                    "companyOrShopPan":"3847294872384"
                },
                "settlement":{
                    "companyBankAccountNumber":"jkshd384729384",
                    "bankIfscCode":"b43bo34432",
                    "companyBankName":"3428237498723",
                    "bankBranchName":"4234234234",
                    "bankAccountName":"348729847"
                },
                "emailId":"dsaasdasd",
                "shopAndPanImage":"3847923874823",
                "cancellationCheckImages":"3742983749823",
                "ekycDocuments":"347298347",
                "merchantPinCode":"4763284623",
                "tan":"4389749823",
                "merchantCityName":"9834792834",
                "merchantDistrictName":"472983478932"
            }]
        }
    
    def decodeJwt(self,data):
        return jwt.decode(data,self.paySprintKey,algorithms=['HS256'])