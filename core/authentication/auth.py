import jwt
from datetime import datetime
class Authentication:
    def __init__(self, auth,app):
        self.auth = auth
        self.app = app

    def verifyToken(self, data):
        
        if data['token'] is None:
            return {'error': 'Token is required'}, 400
        try:
            decoded_token = self.auth.verify_id_token(data['token'], check_revoked=True)
            uid = decoded_token['uid']
        except Exception as e:
            return {'error': 'Invalid token'}, 400
        if (uid==data['uid']):
            return {'uid': uid}, 200
        else:
            return {'error': 'Invalid token'}, 400
    
    


if __name__ == '__main__':
    testClass = Authentication()

    @testClass.verifyToken
    def func(number, data='gdfsdf'):
        print(number, data)
