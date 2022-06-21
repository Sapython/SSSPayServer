import json
import requests
from core.authentication.paysprintAuth import PaySprintAuth
# This class is used to recharge LPG gas cylinders
class LPG:
    def __init__(self,app):
        """
        It initializes the headers, operatorListUrl, fetchLpgDetailsUrl, rechargeLPGUrl and statusUrl
        
        :param name: The name of the LPG operator
        :param price: The amount you want to recharge
        :param quantity: The amount of gas you want to refill
        """
        self.auth = PaySprintAuth(app)
        self.operatorListUrl = 'https://paysprint.in/service-api/api/v1/service/bill-payment/lpg/getoperator'
        self.fetchLpgDetailsUrl = 'https://paysprint.in/service-api/api/v1/service/bill-payment/lpg/fetchbill'
        self.rechargeLPGUrl = 'https://paysprint.in/service-api/api/v1/service/bill-payment/lpg/paybill'
        self.statusUrl  = 'https://paysprint.in/service-api/api/v1/service/bill-payment/lpg/status'
    
    def getOperatorList(self,mode:str):
        """
        It takes a mode as a parameter and returns a list of operators based on the mode
        
        :param mode: The mode of the operator. It can be either online or offline
        :type mode: str
        :return: a dictionary with the response code and the list of operators.
        """
        if mode != 'online' and mode != 'offline':
            return {'error': 'Invalid mode'}, 400
        payload = json.dumps({"mode":mode})
        headers = self.auth.generatePaysprintAuthHeaders()
        print(headers)
        response = requests.request(
            "POST", self.operatorListUrl, headers=headers)
        print(response.json())
        if (response.json()['response_code'] == 1):
            return response.json()
        else:
            return {'error': response.json()}, 400
    
    def fetchLpgDetails(self,caNumber:int,operatorNo:int):
        """
        It takes two parameters, caNumber and operatorNo, and returns a json response
        
        :param caNumber: Consumer Account Number
        :type caNumber: int
        :param operatorNo: The operator number of the LPG company
        :type operatorNo: int
        :return: The response is being returned.
        """
        payload = json.dumps({"canumber":caNumber,"operator":operatorNo})
        response = requests.request(
            "POST", self.fetchLpgDetailsUrl, headers=self.auth.generatePaysprintAuthHeaders(), data=payload)
        if (response.json()['response_code'] == 1):
            return response.json()
        else:
            return {'error': 'Cannot fetch bill details. Try again later'}, 400
    
    def rechargeLpg(self,caNumber:int,operatorNo:int,amount:int,ad1:int,ad2:int,ad3:int,referenceId:int,latitude:float,longitude:float):
        """
        It takes in a bunch of parameters and returns a response.json if the response code is 1, else it
        returns an error
        
        :param caNumber: Consumer Account Number
        :type caNumber: int
        :param operatorNo: 1 for Indane, 2 for HP, 3 for Bharat Gas
        :type operatorNo: int
        :param amount: Amount to be recharged
        :type amount: int
        :param ad1: Consumer Number
        :type ad1: int
        :param ad2: Consumer Number
        :type ad2: int
        :param ad3: This is the consumer number
        :type ad3: int
        :param referenceId: This is a unique reference id that you generate for each recharge. This is
        used to track the recharge
        :type referenceId: int
        :param latitude: float
        :type latitude: float
        :param longitude: float
        :type longitude: float
        :return: The response is being returned.
        """
        payload = json.dumps({"canumber":caNumber,"operator":operatorNo,"amount":amount,"ad1":ad1,"ad2":ad2,"ad3":ad3,"referenceid":referenceId,"latitude":latitude,"longitude":longitude})
        response = requests.request(
            "POST", self.rechargeLpgUrl, headers=self.auth.generatePaysprintAuthHeaders(), data=payload)
        if (response.json()['response_code'] == 1):
            return response.json()
        else:
            return {'error': 'Cannot recharge. Try again later'}, 400
    
    def getLpgRechargeStatus(self,referenceId:str):
        """
        It takes a referenceId as a parameter and returns the status of the recharge
        
        :param referenceId: The reference id of the transaction
        :type referenceId: str
        :return: The response is being returned.
        """
        payload = json.dumps({"referenceid":referenceId})
        response = requests.request(
            "POST", self.statusUrl, headers=self.auth.generatePaysprintAuthHeaders(), data=payload)
        if (response.json()['response_code'] == 1):
            return response.json()
        else:
            try:
                return {'error':response.json()['message'] }, 400
            except:
                return {'error': 'Cannot fetch status. Try again later'}, 400
