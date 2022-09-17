import json
import requests
from core.authentication.paysprintAuth import PaySprintAuth

class Recharge:
    def __init__(self,app):
        """
        This function is used to initialize the header, operatorListUrl, doRechargeUrl and
        statusEnquiryUrl
        
        :param client: The client's phone number
        :param amount: The amount to be recharged
        :param card_number: The card number of the card you want to use
        :param card_cvv: The 3-digit CVV number on the back of your card
        :param card_expiration_date: The expiration date of the card. It should be in the format MM/YYYY
        """
        self.auth = PaySprintAuth(app)
        self.operatorListUrl = 'https://api.paysprint.in/api/v1/service/recharge/recharge/getoperator'
        self.doRechargeUrl = 'https://api.paysprint.in/api/v1/service/recharge/recharge/dorecharge'
        self.statusEnquiryUrl = 'https://api.paysprint.in/api/v1/service/recharge/recharge/status'

    def getOperatorList(self):
        """
        It makes a POST request to the operatorListUrl and returns the response in JSON format
        :return: The response is being returned.
        """
        response = requests.request(
            "POST", self.operatorListUrl, headers=self.auth.generatePaysprintAuthHeaders())
        # print(response.json())
        if (response.json()['responsecode'] == 1):
            return response.json()
        else:
            return {'error': 'Cannot fetch operators. Try again later'}, 400

    def doRecharge(self,operator:str,caNumber:int,amount:int,referenceId:int):
        """
        It takes in 4 parameters and returns a json response
        
        :param operatorNo: The operator number of the operator you want to recharge
        :type operatorNo: int
        :param caNumber: The customer account number
        :type caNumber: int
        :param amount: Amount to be recharged
        :type amount: int
        :param referenceId: This is a unique reference id that you will generate for each recharge
        request
        :type referenceId: int
        :return: The response is a JSON object.
        """
        payload = {"operator": operator,"canumber": caNumber,"amount": amount,"referenceid": referenceId}
        print(payload)
        response = requests.request(
            "POST", self.doRechargeUrl, headers=self.auth.generatePaysprintAuthHeaders(), json=payload)
        if (response.json()['response_code'] == 1):
            return response.json()
        else:
            return {'error': response.json()['message'],'response_code':response.json()['response_code'],'status':False}, 400
    
    def getStatusEnquiry(self,referenceId:str):
        """
        It takes a referenceId as a parameter and returns a json object with the status of the
        transaction
        
        :param referenceId: The reference ID of the transaction you want to check the status of
        :type referenceId: str
        :return: The response is being returned.
        """
        payload = {"referenceid": referenceId}
        response = requests.request(
            "POST", self.statusEnquiryUrl, headers=self.auth.generatePaysprintAuthHeaders(), json=payload)
        print("response.text",response.text)
        if (response.json()['responsecode'] == 1):
            return response.json()  
        else:
            return {'error': response.json()['message'],'status':False}, 400
