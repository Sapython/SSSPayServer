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
        print("Response",response.json())
        return response.json(), response.status_code

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
            'accessmodetype':'SITE',
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
        print("Response",response.json())
        return response.json(), response.status_code
    

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
            'accessmodetype':'SITE',
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
        # self.logging.info(payload)
        response = requests.post("https://api.paysprint.in/api/v1/service/aeps/cashwithdraw/index",data=payload,headers=self.auth.generatePaysprintAuthHeaders())
        print('-'*20)
        print('Response',response.json())
        print('-'*20)
        return response.json(), response.status_code

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
            'accessmodetype':'SITE',
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
        print('-'*20)
        print('Response',response.json())
        print('-'*20)
        return response.json(), response.status_code
    
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
        print("Response:",response)
        return response.json(), response.status_code

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
        return response.json(), response.status_code
    
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
            'accessmodetype':'SITE',
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
        return response.json(), response.status_code
    
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
        return response.json(), response.status_code