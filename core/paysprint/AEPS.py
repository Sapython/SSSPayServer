import json
import base64
import logging
import requests
import datetime
from core.authentication.encryption import Encrypt
from core.authentication.paysprintAuth import PaySprintAuth
class AEPS:
    def __init__(self,app,development):
        super().__init__()
        self.__aeps_url = "https://api.paysprint.in/api/v1/service/aeps/balanceenquiry/index"
        self.encryption = Encrypt()
        self.logging = logging
        self.auth = PaySprintAuth(app)
        self.subMerchantId = "PS001619"
        self.ipaddress = "34.126.221.178"
        self.development = development

    def encodeBase64(self,data):
        return base64.b64encode(data)
    
    def getBankList(self):
        return requests.post('https://api.paysprint.in/api/v1/service/aeps/banklist/index',headers = self.auth.generatePaysprintAuthHeaders())

    def getBalanceEnquiry(self,latitude:float,longitude:float,mobile_number:str,referenceNo:str,adhaarNumber:str,nationalBankIdentification:int,requestRemarks:str,authData:str,is_iris:str,merchantCode:str):
        if not latitude:
            return {'message': 'Missing latitude'}, 400
        if not longitude:
            return {'message': 'Missing longitude'}, 400
        if not mobile_number:
            return {'message': 'Missing mobile_number'}, 400
        if not referenceNo:
            return {'message': 'Missing referenceNo'}, 400
        if not adhaarNumber:
            return {'message': 'Missing adhaarNumber'}, 400
        if not nationalBankIdentification:
            return {'message': 'Missing nationalBankIdentification'}, 400
        if not authData:
            return {'message': 'Missing authData'}, 400
        if not merchantCode:
            return {'message': 'Missing merchantCode'}, 400
        # if (is_iris):
        #     is_iris= 'Yes'
        # elif (is_iris==False):
        #     is_iris= 'No'
        # else:
        #     return {'message': 'Missing is_iris'}, 400
        data = {
            'latitude':str(latitude),
            'longitude':str(longitude),
            'mobilenumber':str(mobile_number),
            'referenceno':str(referenceNo),
            'ipaddress':self.ipaddress,
            'adhaarnumber':str(adhaarNumber),
            'accessmodetype':'APP',
            'nationalbankidentification':nationalBankIdentification,
            'requestremarks':str(requestRemarks),
            'data':authData,
            'pipe':'bank2',
            'timestamp':str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            "transactiontype":'BE',
            "submerchantid":merchantCode,
            "is_iris":is_iris
        }
        print("Request",data)
        # self.logging.info("aepsData "+str(data))
        encoded = self.encryption.encrypt(json.dumps(data).encode('utf-8'))
        payload = {
            "body":encoded
        }
        # self.logging.info(payload)
        headers = self.auth.generatePaysprintAuthHeaders()
        response = requests.post("https://api.paysprint.in/api/v1/service/aeps/balanceenquiry/index",data=payload,headers=headers)
        if ('application/json' in response.headers.get('Content-Type', '')):
            print('Response',response.json())
            print('-'*20)
            return response.json(), response.status_code, True
        else:
            print('Response',response.content)
            print('-'*20)
            return str(response.content), response.status_code, False

    def getBalanceEnquiryTest(self,latitude:float,longitude:float,mobile_number:str,referenceNo:str,adhaarNumber:str,nationalBankIdentification:int,requestRemarks:str,authData:str,is_iris:str,merchantCode:str):
        if not latitude:
            return {'message': 'Missing latitude'}, 400
        if not longitude:
            return {'message': 'Missing longitude'}, 400
        if not mobile_number:
            return {'message': 'Missing mobile_number'}, 400
        if not referenceNo:
            return {'message': 'Missing referenceNo'}, 400
        if not adhaarNumber:
            return {'message': 'Missing adhaarNumber'}, 400
        if not nationalBankIdentification:
            return {'message': 'Missing nationalBankIdentification'}, 400
        if not authData:
            return {'message': 'Missing authData'}, 400
        if not merchantCode:
            return {'message': 'Missing merchantCode'}, 400
        # if (is_iris):
        #     is_iris= 'Yes'
        # elif (is_iris==False):
        #     is_iris= 'No'
        # else:
        #     return {'message': 'Missing is_iris'}, 400
        data = {
            'latitude':str(latitude),
            'longitude':str(longitude),
            'mobilenumber':str(mobile_number),
            'referenceno':str(referenceNo),
            'ipaddress':self.ipaddress,
            'adhaarnumber':str(adhaarNumber),
            'accessmodetype':'APP',
            'nationalbankidentification':nationalBankIdentification,
            'requestremarks':str(requestRemarks),
            'data':authData,
            'pipe':'bank2',
            'timestamp':str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            "transactiontype":'BE',
            "submerchantid":merchantCode,
            "is_iris":is_iris
        }
        print("Request",data)
        # self.logging.info("aepsData "+str(data))
        encoded = self.encryption.encrypt(json.dumps(data).encode('utf-8'))
        payload = {
            "body":encoded
        }
        # self.logging.info(payload)
        headers = self.auth.generatePaysprintAuthHeaders()
        response = requests.post("https://api.paysprint.in/api/v1/service/aeps/balanceenquiry/index",data=payload,headers=headers)
        if ('application/json' in response.headers.get('Content-Type', '')):
            print('Response',response.json())
            print('-'*20)
            return response.json(), response.status_code, True
        else:
            print('Response',response.content)
            print('-'*20)
            return str(response.content), response.status_code, False
    

    def withdrawCash(self,latitude:float,longitude:float,mobile_number:str,referenceNo:str,adhaarNumber:str,nationalBankIdentification:int,requestRemarks:str,authData:str,amount:int,is_iris:str,merchantCode:str):
        if not latitude:
            return {'message': 'Missing latitude'}, 400
        if not longitude:
            return {'message': 'Missing longitude'}, 400
        if not mobile_number:
            return {'message': 'Missing mobile_number'}, 400
        if not referenceNo:
            return {'message': 'Missing referenceNo'}, 400
        if not adhaarNumber:
            return {'message': 'Missing adhaarNumber'}, 400
        if not nationalBankIdentification:
            return {'message': 'Missing nationalBankIdentification'}, 400
        if not authData:
            return {'message': 'Missing authData'}, 400
        if not amount:
            return {'message': 'Missing amount'}, 400
        data = {
            'latitude':str(latitude),
            'longitude':str(longitude),
            'mobilenumber':str(mobile_number),
            'referenceno':str(referenceNo),
            'ipaddress':str(self.ipaddress),
            'adhaarnumber':str(adhaarNumber),
            'accessmodetype':'APP',
            'nationalbankidentification':str(nationalBankIdentification),
            'requestremarks':str(requestRemarks),
            'data':authData,
            'pipe':'bank2',
            'timestamp':str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            "transactiontype":'CW',
            "submerchantid":merchantCode,
            "amount":int(amount),
            "is_iris":is_iris
        }
        print('-'*20)
        print('Request',data)
        print('-'*20)
        # self.logging.info("aepsData"+str(data))
        encoded = self.encryption.encrypt(json.dumps(data).encode('utf-8'))
        payload = {
            "body":encoded
        }
        # fakeData = {
        #     "name": "SUMIT SETH",
        #     "last_aadhar": "3327",
        #     "bankiin": "608032",
        #     "status": True,
        #     "errorcode": "0",
        #     "message": "AEPS Transaction Success",
        #     "mobile": "8604863246",
        #     "clientrefno": "595788604863246",
        #     "balanceamount": "12.09",
        #     "bankrrn": "301319095611",
        #     "amount": 100,
        #     "ackno": 39576647,
        #     "response_code": 1
        # }
        # return fakeData, 200, True
        # self.logging.info(payload)
        response = requests.post("https://api.paysprint.in/api/v1/service/aeps/cashwithdraw/index",data=payload,headers=self.auth.generatePaysprintAuthHeaders())
        print('-'*20)
        print("Response status",response.status_code)
        print("Response json",response.headers)
        if ('application/json' in response.headers.get('Content-Type', '')):
            try:
                print('Response',response.json())
                print('-'*20)
                return response.json(), response.status_code, True
            except:
                print('Response exception',response.content)
                print('-'*20)
                if (response.status_code == 200):
                    return str(response.content), response.status_code, True
                else:
                    return str(response.content), response.status_code, False
        else:
            print('Response exception elsed',str(response.content))
            print('-'*20)
            return str(response.content), response.status_code, False

    def getMiniStatement(self,latitude:float,longitude:float,mobile_number:str,referenceNo:str,adhaarNumber:str,nationalBankIdentification:int,requestRemarks:str,authData:str,is_iris:str,merchantCode:str):
        if not latitude:
            return {'message': 'Missing latitude'}, 400
        if not longitude:
            return {'message': 'Missing longitude'}, 400
        if not mobile_number:
            return {'message': 'Missing mobile_number'}, 400
        if not referenceNo:
            return {'message': 'Missing referenceNo'}, 400
        if not adhaarNumber:
            return {'message': 'Missing adhaarNumber'}, 400
        if not nationalBankIdentification:
            return {'message': 'Missing nationalBankIdentification'}, 400
        if not authData:
            return {'message': 'Missing authData'}, 400
        data = {
            'latitude':str(latitude),
            'longitude':str(longitude),
            'mobilenumber':str(mobile_number),
            'referenceno':str(referenceNo),
            'ipaddress':str(self.ipaddress),
            'adhaarnumber':str(adhaarNumber),
            'accessmodetype':'APP',
            'nationalbankidentification':nationalBankIdentification,
            'requestremarks':requestRemarks,
            'data':authData,
            'pipe':'bank2',
            'timestamp':datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "transactiontype":"MS",
            "submerchantid":merchantCode,
            "is_iris":is_iris
        }
        print('-'*20)
        print('Request',data)
        print('-'*20)
        print("DataDump",json.dumps(data).encode('utf-8'),type(json.dumps(data).encode('utf-8')))
        if self.development: print("DATA",data)
        self.logging.info("aepsData"+str(data))
        encoded = self.encryption.encrypt(json.dumps(data).encode('utf-8'))
        payload = {
            "body":encoded
        }
        if self.development: print(payload)
        self.logging.info(payload)    
        response = requests.post("https://api.paysprint.in/api/v1/service/aeps/ministatement/index",data=payload,headers=self.auth.generatePaysprintAuthHeaders())
        if ('application/json' in response.headers.get('Content-Type', '')):
            print('Response',response.json())
            print('-'*20)
            return response.json(), response.status_code, True
        else:
            print('Response',response.content)
            print('-'*20)
            return str(response.content), response.status_code, False
    
    def getCashWithdrawStatus(self,referenceNo:str):
        if not referenceNo:
            return {'message': 'Missing referenceNo'}, 400
        data = {
            'reference':referenceNo
        }
        # self.logging.info("aepsData"+str(data))
        encoded = self.encryption.encrypt(json.dumps(data).encode('utf-8'))
        payload = {
            "body":encoded
        }
        # self.logging.info(payload)
        response = requests.post("https://api.paysprint.in/api/v1/service/aeps/aepsquery/query",json=payload,headers=self.auth.generatePaysprintAuthHeaders())
        logging.info(response)
        if ('application/json' in response.headers.get('Content-Type', '')):
            print('Response',response.json())
            print('-'*20)
            return response.json(), response.status_code, True
        else:
            print('Response',response.content)
            print('-'*20)
            return str(response.content), response.status_code, False

    def withdrawThreeWay(self,referenceId:str,status:str):
        if not referenceId:
            return {'message': 'Missing referenceId'}, 400
        if not status:
            return {'message': 'Missing status'}, 400
        data = {
            'reference':referenceId,
            'status':status
        }
        # self.logging.info("aepsData"+str(data))
        print("DATA",data)
        encoded = self.encryption.encrypt(json.dumps(data).encode('utf-8'))
        payload = {
            "body":encoded
        }
        # self.logging.info(payload)
        response = requests.post("https://api.paysprint.in/api/v1/service/aeps/threeway/threeway",json=payload,headers=self.auth.generatePaysprintAuthHeaders())
        return response.json(), response.status_code, True
    
    def aadhaarPay(self,latitude:float,longitude:float,mobile_number:str,referenceNo:str,adhaarNumber:str,nationalBankIdentification:int,requestRemarks:str,authData:str,is_iris:str,merchantCode:str):
        if not latitude:
            return {'message': 'Missing latitude'}, 400
        if not longitude:
            return {'message': 'Missing longitude'}, 400
        if not mobile_number:
            return {'message': 'Missing mobile_number'}, 400
        if not referenceNo:
            return {'message': 'Missing referenceNo'}, 400
        if not adhaarNumber:
            return {'message': 'Missing adhaarNumber'}, 400
        if not nationalBankIdentification:
            return {'message': 'Missing nationalBankIdentification'}, 400
        if not authData:
            return {'message': 'Missing authData'}, 400
        data = {
            'latitude':str(latitude),
            'longitude':str(longitude),
            'mobilenumber':str(mobile_number),
            'referenceno':str(referenceNo),
            'ipaddress':str(self.ipaddress),
            'adhaarnumber':str(adhaarNumber),
            'accessmodetype':'APP',
            'nationalbankidentification':nationalBankIdentification,
            'requestremarks':requestRemarks,
            'amount':1,
            'data':authData,
            'pipe':'bank2',
            'timestamp':datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "transactiontype":"MS",
            "submerchantid":merchantCode,
            "is_iris":is_iris
        }
        print("DataDump",json.dumps(data).encode('utf-8'),type(json.dumps(data).encode('utf-8')))
        if self.development: print("DATA",data)
        # self.logging.info("aepsData"+str(data))
        encoded = self.encryption.encrypt(json.dumps(data).encode('utf-8'))
        payload = {
            "body":encoded
        }
        if self.development: print(payload)
        self.logging.info(payload)    
        response = requests.post("https://api.paysprint.in/api/v1/service/aadharpay/aadharpay/index",json=payload,headers=self.auth.generatePaysprintAuthHeaders())
        if ('application/json' in response.headers.get('Content-Type', '')):
            print('Response',response.json())
            print('-'*20)
            return response.json(), response.status_code, True
        else:
            print('Response',response.content)
            print('-'*20)
            return str(response.content), response.status_code, False
    
    def getAadhaarPaymentStatus(self,referenceId:str):
        if not referenceId:
            return {'message': 'Missing parameters'}, 400
        data = {
            'reference':referenceId
        }
        print("DATA",data)
        logging.info("aepsData"+str(data))
        encoded = self.encryption.encrypt(json.dumps(data).encode('utf-8'))
        print(self.encodeBase64(encoded))
        payload = {
            "body":self.encodeBase64(encoded).decode()
        }
        logging.info(payload)
        response = requests.get("https://api.paysprint.in/api/v1/service/aadharpay/aadharpayquery/query",json=payload,headers=self.auth.generatePaysprintAuthHeaders())
        if ('application/json' in response.headers.get('Content-Type', '')):
            print('Response',response.json())
            print('-'*20)
            return response.json(), response.status_code, True
        else:
            print('Response',response.content)
            print('-'*20)
            return str(response.content), response.status_code, False