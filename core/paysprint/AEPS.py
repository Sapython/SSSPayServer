import json
import base64
import requests
from core.authentication.encryption import Encrypt
from core.authentication.paysprintAuth import PaySprintAuth
class AEPS:
    def __init__(self,app):
        super().__init__()
        self.__aeps_url = "https://paysprint.in/service-api/api/v1/service/aeps/balanceenquiry/index"
        self.encryption = Encrypt()
        self.auth = PaySprintAuth(app)

    def encodeBase64(data):
        return base64.b64encode(data)
    
    def getBalance(self,latitude:float,longitude:float,mobile_number:str,referenceNo:str,ipaddress:str,adhaarNumber:str,accessModeType:str,nationalBankIdentification:int,requestRemarks:str,data:str,pipe:str,timestamp:str,transactionType:str,subMerchantId:str,is_iris:str):
        data = {
            'latitude':latitude,
            'longitude':longitude,
            'mobile_number':mobile_number,
            'referenceno':referenceNo,
            'ipaddress':ipaddress,
            'adhaarnumber':adhaarNumber,
            'accessmodetype':accessModeType,
            'nationalbankidentification':nationalBankIdentification,
            'requestremarks':requestRemarks,
            'data':data,
            'pipe':pipe,
            'timestamp':timestamp,
            "transactiontype":transactionType,
            "submerchantid":subMerchantId,
            "is_iris":is_iris
        }
        encoded = self.encryption.encrypt(json.dumps(data).encode('utf-8'))
        print('DATA: ',encoded)
        print('DATA: ',base64.b64encode(encoded).decode())
        pass