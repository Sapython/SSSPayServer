import json
import requests
from core.authentication.paysprintAuth import PaySprintAuth


class LIC:
    def __init__(self, app):
        """
        It's a constructor for the class
        """
        self.auth = PaySprintAuth(app)
        self.fetchLic = 'https://api.paysprint.in/api/v1/service/bill-payment/bill/fetchlicbill'
        self.payLicBillUrl = 'https://api.paysprint.in/api/v1/service/bill-payment/bill/paylicbill'
        self.licStatus = 'https://api.paysprint.in/api/v1/service/bill-payment/bill/licstatus'

    def fetchLicBill(self, caNumber: int, email: str, mode: str):
        """
        It takes in a caNumber, email and mode and returns a json response from the API

        :param caNumber: The CA number of the customer
        :type caNumber: int
        :param email: email address of the user
        :type email: str
        :param mode: online/offline
        :type mode: str
        :return: The response is being returned.
        """
        if mode != 'online' and mode != 'offline':
            return {'error': 'Invalid mode'}, 400
        payload = {"canumber": caNumber, "email": email, "mode": mode}
        print('-' * 50)
        print("Request",payload)
        print('-' * 50)
        response = requests.request(
            "POST", self.fetchLic, headers=self.auth.generatePaysprintAuthHeaders(), json=payload)
        print(response.json())

        if (response.json()['response_code'] == 1):
            return response.json(), 200
        else:
            return response.json(), 400

    def payLicBill(self, caNumber: int, mode: str, amount: int, email: str, referenceId: int, latitude: float, longitude: float, billFetch: dict):
        """
        This function is used to pay LIC bill

        :param caNumber: int, mode: str, amount: int, email: str, policyNumber1: str, policyNumber2:
        str, referenceId: int, latitude: float, longitude: float, billNo: str, bilAmount: str,
        billNetAmount: str, billDate: str
        :type caNumber: int
        :param mode: online/offline
        :type mode: str
        :param amount: Amount to be paid
        :type amount: int
        :param email: email address of the customer
        :type email: str
        :param policyNumber1: Policy Number
        :type policyNumber1: str
        :param policyNumber2: str, referenceId: int, latitude: float, longitude: float, billNo: str,
        bilAmount: str, billNetAmount: str, billDate: str, acceptPayment: bool, acceptPartPay: bool,
        cellNumber: str, dueFrom: str, due
        :type policyNumber2: str
        :param referenceId: This is a unique reference id that you generate for each transaction
        :type referenceId: int
        :param latitude: float, longitude: float, billNo: str, bilAmount: str, billNetAmount: str,
        billDate: str, acceptPayment: bool, acceptPartPay: bool, cellNumber: str, dueFrom: str, dueTo:
        str, validationId: str,
        :type latitude: float
        :param longitude: float, latitude: float, billNo: str, bilAmount: str, billNetAmount: str,
        billDate: str, acceptPayment: bool, acceptPartPay: bool, cellNumber: str, dueFrom: str, dueTo:
        str, validationId: str, bill
        :type longitude: float
        :param billNo: The bill number
        :type billNo: str
        :param bilAmount: Amount of the bill
        :type bilAmount: str
        :param billNetAmount: The amount to be paid
        :type billNetAmount: str
        :param billDate: str, acceptPayment: bool, acceptPartPay: bool, cellNumber: str, dueFrom: str,
        dueTo: str, validationId: str, billId: str
        :type billDate: str
        :param acceptPayment: True/False
        :type acceptPayment: bool
        :param acceptPartPay: bool,
        :type acceptPartPay: bool
        :param cellNumber: str, dueFrom: str, dueTo: str, validationId: str, billId: str
        :type cellNumber: str
        :param dueFrom: The date from which the bill is due
        :type dueFrom: str
        :param dueTo: str, validationId: str, billId: str
        :type dueTo: str
        :param validationId: This is the validationId that you get from the getLicBillDetails API
        :type validationId: str
        :param billId: This is the unique ID of the bill
        :type billId: str
        :return: The response is a JSON object.
        """
        if mode != 'online' and mode != 'offline':
            return {'error': 'Invalid mode'}, 400
        payload = {"canumber": caNumber, "mode": mode, "amount": amount, "ad1": email, "referenceid": referenceId, "latitude": latitude, "longitude": longitude, "bill_fetch": billFetch}
        print('-' * 50)
        print("Request",payload)
        print('-' * 50)
        response = requests.request(
            "POST", self.payLicBillUrl, headers=self.auth.generatePaysprintAuthHeaders(), json=payload)
        print('-' * 50)
        print("Response",response.json())
        print('-' * 50)
        if (response.json()['response_code'] == 1):
            return response.json()
        else:
            return response.json()

    def getLicStatus(self, referenceId: str):
        """
        It takes a referenceId as a parameter and returns the status of the license

        :param referenceId: The reference id of the transaction
        :type referenceId: str
        :return: The response is being returned.
        """
        payload = {"referenceid": referenceId}
        print('-' * 50)
        print("Request",payload)
        print('-' * 50)
        response = requests.request(
            "GET", self.licStatus,json=payload, headers=self.auth.generatePaysprintAuthHeaders())
        print('-' * 50)
        print("Response",response.json())
        print('-' * 50)
        if (response.json()['response_code'] == 1):
            return response.json()
        else:
            return response.json()
