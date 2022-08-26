import json
import requests
from core.authentication.paysprintAuth import PaySprintAuth
# A class that has methods that make requests to a URL and return a response.
class BillPayment:
    def __init__(self,app):
        """
        A constructor function. It is called when an object of the class is created.

        :param billPayment: This is the object of the BillPayment class
        """
        self.operatorList = 'https://paysprint.in/service-api/api/v1/service/bill-payment/bill/getoperator'
        self.fetchBillDetailsUrl = 'https://paysprint.in/service-api/api/v1/service/bill-payment/bill/fetchbill'
        self.payBillUrl = 'https://paysprint.in/service-api/api/v1/service/bill-payment/bill/paybill'
        self.statusEnquiryUrl = 'https://paysprint.in/service-api/api/v1/service/bill-payment/bill/status'
        self.auth = PaySprintAuth(app)

    def getOperatorList(self, mode: str):
        """
        It returns a list of operators based on the mode passed to it

        :param mode: This is the mode of the transaction. It can be either online or offline
        :type mode: str
        :return: The response is being returned.
        """
        if mode != 'online' and mode != 'offline':
            return {'error': 'Invalid mode'}, 400
        payload = json.dumps({"mode": mode})
        response = requests.request(
            "POST", self.operatorList, headers=self.auth.generatePaysprintAuthHeaders(), data=payload)
        if (response.json()['response_code'] == 1):
            return response.json()
        else:
            return response.json()

    def fetchBillDetails(self, operatorNo: int, caNumber: int, mode: str):
        """
        It takes in the operator number, the CA number and the mode (online/offline) and returns the
        bill details

        :param operatorNo: The operator number of the operator you want to fetch the bill details for
        :type operatorNo: int
        :param caNumber: The CA number of the customer
        :type caNumber: int
        :param mode: online or offline
        :type mode: str
        :return: a tuple.
        """
        if mode != 'online' and mode != 'offline':
            return {'error': 'Invalid mode'}
        payload = json.dumps(
            {"operator": operatorNo, "canumber": caNumber, "mode": mode})
        response = requests.request(
            "POST", self.fetchBillDetailsUrl, headers=self.auth.generatePaysprintAuthHeaders(), data=payload)
        if (response.json()['response_code'] == 1):
            return response.json()
        else:
            return response.json()

    def payBill(self, operatorNo: str, caNumber: str, amount: str, referenceNo: str, latitude: str, longitude: str, billFetched:dict):
        """
        I'm trying to send a POST request to a URL with a JSON payload

        :param operatorNo: The operator number you want to pay the bill for
        :type operatorNo: str
        :param caNumber: Consumer Account Number
        :type caNumber: str
        :param amount: Amount to be paid
        :type amount: str
        :param referenceNo: This is the unique reference number that you generate for each transaction
        :type referenceNo: str
        :param latitude: Latitude of the location where the transaction is being made
        :type latitude: str
        :param longitude: str,
        :type longitude: str
        :param mode: online
        :type mode: str
        :param billAmount: Total bill amount
        :type billAmount: str
        :param billNetAmount: The amount to be paid
        :type billNetAmount: str
        :param billDate: The date of the bill
        :type billDate: str
        :param dueDate: The due date of the bill
        :type dueDate: str
        :param acceptPayment: If the bill is paid in full, set this to true. If the bill is paid
        partially, set this to false
        :type acceptPayment: bool
        :param acceptPartPay: bool,
        :type acceptPartPay: bool
        :param cellNumber: str,
        :type cellNumber: str
        :param userName: Name of the user
        :type userName: str
        :return: The response is a JSON object.
        """
        payload = json.dumps({
            "operator": operatorNo,
            "canumber": caNumber,
            "amount": amount,
            "referenceid": referenceNo,
            "latitude": latitude,
            "longitude": longitude,
            "mode": "online",
            "bill_fetch": billFetched
        })
        response = requests.request(
            "POST", self.payBillUrl, headers=self.auth.generatePaysprintAuthHeaders(), data=payload)
        if (response.json()['response_code'] == 1):
            return response.json()
        else:
            return response.json()

    def statusEnquiry(self, referenceId: str):
        """
        It takes a referenceId as a parameter and returns a json response

        :param referenceId: The reference ID of the transaction you want to check the status of
        :type referenceId: str
        :return: The response is being returned.
        """
        payload = json.dumps({"referenceid": referenceId})
        response = requests.request(
            "POST", self.statusEnquiryUrl, headers=self.auth.generatePaysprintAuthHeaders(), data=payload)
        if (response.json()['status'] == True and response.json()['data']['status'] == '1'):
            return response.json()
        else:
            return response.json()
