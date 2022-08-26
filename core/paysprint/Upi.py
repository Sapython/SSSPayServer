import requests
class UPI:
    def __init__(self, app):
        self.app = app
        self.key = 'd6755646-02c9-42e1-b236-b5cf44e5b1f0'

    def createOrder(self, amount: str, transactionId: str, customerName: str, customerEmail: str, customerMobile: str):
        data = {
            "key": self.key,
            "client_txn_id": transactionId,
            "amount": str(amount),
            "p_info": "Payout",
            "customer_name": customerName,
            "customer_email": customerEmail,
            "customer_mobile": str(customerMobile),
            "redirect_url":'https://ssspay.in'
        }
        print("Sent request",data)
        response = requests.post('https://merchant.upigateway.com/api/create_order', json=data)
        print(response.json())
        return response.json()
