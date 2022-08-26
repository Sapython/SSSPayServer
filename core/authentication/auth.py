import jwt
from datetime import datetime
from firebase_admin import firestore

class Authentication:
    def __init__(self, auth,app):
        self.auth = auth
        self.app = app
        self.firestore = firestore.client()

    def verifyToken(self, data):
        
        if data['token'] is None:
            return {'error': 'Token is required'}, 400
        try:
            decoded_token = self.auth.verify_id_token(data['token'], check_revoked=True)
            uid = decoded_token['uid']
            userDatabase = self.firestore.collection('users').document(uid).get().to_dict()
            if (data['access'] != userDatabase['access']['access']):
                return {'message': 'Operation not allowed'}, 200
            if (data['status']!='active'):
                return {'message': 'Inactive user cannot perform this operation. Contact admin for support.'}, 200
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
