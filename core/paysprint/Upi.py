import requests
from datetime import date, datetime
class UPI:
    def __init__(self, app):
        self.app = app
        self.key = 'd6755646-02c9-42e1-b236-b5cf44e5b1f0'

    def createOrder(self, amount: str, transactionId: str, customerName: str, customerEmail: str, customerMobile: str,userId:str):
        data = {
            "key": self.key,
            "client_txn_id": transactionId,
            "amount": str(amount),
            "p_info": "Payout",
            "customer_name": customerName,
            "customer_email": customerEmail,
            "customer_mobile": str(customerMobile),
            "redirect_url":'https://ssspay-prod.web.app/r/'+str(transactionId)+'_'+str(userId)+'_'+ datetime.now().strftime("%d-%m-%Y"),
        }
        print("Sent request",data)
        response = requests.post('https://merchant.upigateway.com/api/create_order', json=data)
        print("--------")
        print("Received",response.json())
        print("--------")
        return response.json()
    
    def checkStatus(self, transactionId,txn_date):
        if not transactionId:
            return {'error': True, 'message': 'Transaction ID not found'}, 400
        if not txn_date:
            return {'error': True, 'message': 'Transaction Date not found'}, 400

        data = {
            "key": self.key,
            "client_txn_id": transactionId,
            "txn_date": txn_date
        }
        print('========')
        print(data)
        print('========')
        return requests.post('https://merchant.upigateway.com/api/check_order_status',json = data)
