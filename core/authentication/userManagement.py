import datetime
import string
import random
from core.authentication.encryption import Encrypt
from core.authentication.paysprintAuth import PaySprintAuth
from firebase_admin import firestore
from core.messaging.messaging import Messaging

class UserManagement:
    def __init__(self, auth, app):
        super().__init__()
        self.app = app
        self.messaging = Messaging()
        self.encryption = Encrypt()
        self.firestore = firestore.client()
        self.auth = auth
        self.accessLevels = ['guest','blocked', 'retailer', 'distributor',
                             'masterDistributor', 'superDistributor', 'admin']

    def unblockUser(self, userId, blockedId):
        if not (userId and blockedId):
            return {'error': 'Missing parameters'}, 400
        user = self.firestore.collection('users').document(userId)
        doc = user.get()
        if doc.exists:
            data = doc.to_dict()
            if data['access']['access'] in ['admin']:
                self.firestore.collection('users').document(
                    blockedId).update({'status': {'access': 'active'},'access': {'access': 'guest'}})
                self.auth.update_user(blockedId, disabled=False)
                return {'message': 'User unblocked successfully'}
            else:
                return {'error': 'Access level insufficient'}, 400
        else:
            return {'error': 'User does not exist'}, 400

    def blockUser(self, authRequest, blockId):
        user = self.firestore.collection('users').document(authRequest['uid'])
        doc = user.get()
        if doc.exists:
            data = doc.to_dict()
            if data['access']['access'] in ['admin']:
                docRef = self.firestore.collection('users').document(blockId)
                docRef.update({'status': {'access': 'blocked'},'access':{'access':'blocked'}})
                self.auth.update_user(blockId, disabled=True)
                return {'message': 'User blocked successfully'}
            else:
                return {'error': 'Access level insufficient'}, 400
        else:
            return {'error': 'User does not exist'}, 400

    def deleteUser(self, userID, deleteUserId):
        if not (userID and deleteUserId):
            return {'error': 'Missing parameters'}, 400
        user = self.firestore.collection('users').document(userID)
        doc = user.get()
        if doc.exists:
            data = doc.to_dict()
            if data['access']['access'] in ['admin']:
                self.firestore.collection(
                    'users').document(deleteUserId).delete()
                self.auth.delete_user(deleteUserId)
                return {'message': 'User deleted successfully'}
            else:
                return {'error': 'Access level insufficient'}, 400
        else:
            return {'error': 'User does not exist'}, 400

    def changeAccess(self, accessLevel, userId, requestUserId):
        if not (accessLevel and userId and requestUserId):
            return {'error': 'Missing parameters'}, 400
        user = self.firestore.collection('users').document(requestUserId).get()
        data = user.to_dict()
        if not user.exists:
            return {'error': 'Not Authorized'}, 400
        if not data['access']['access'] in ['admin']:
            return {'error': 'Action not allowed'}, 400
        user = self.firestore.collection('users').document(userId)
        doc = user.get()
        if doc.exists:
            data = doc.to_dict()
            if accessLevel in self.accessLevels:
                user.update({
                    'access': {'access': accessLevel}
                })
                return {'message': 'Access level changed successfully', 'requestCode': 1}
            else:
                return {'error': 'Invalid access level requested', 'requestCode': 3}, 400
        else:
            return {'error': 'User does not exist', 'requestCode': 4}, 400

    def createUser(self, userData: dict):
        if not userData['uid']:
            return {'error': 'Missing uid'}, 400
        if not userData['displayName']:
            return {'error': 'Missing displayName'}, 400
        if not userData['email']:
            return {'error': 'Missing email'}, 400
        if not userData['phoneNumber']:
            return {'error': 'Missing phoneNumber'}, 400
        if not userData['dob']:
            return {'error': 'Missing dob'}, 400
        if not userData['photoURL']:
            return {'error': 'Missing photoURL'}, 400
        if not userData['aadhaarNumber']:
            return {'error': 'Missing aadhaarNumber'}, 400
        if not userData['panNumber']:
            return {'error': 'Missing panNumber'}, 400
        if not userData['gender']:
            return {'error': 'Missing gender'}, 400
        if not userData['access']:
            return {'error': 'Missing access'}, 400
        if not userData['state']:
            return {'error': 'Missing state'}, 400
        if not userData['city']:
            return {'error': 'Missing city'}, 400
        if not userData['pincode']:
            return {'error': 'Missing pincode'}, 400
        if not userData['address']:
            return {'error': 'Missing address'}, 400
        # if not userData['confirmPassword'] == userData['password']:
        #     return {'error': 'Passwords do not match'}, 400
        # generate random password
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
        splittedDob = userData['dob'].split('-')
        data = {
            "displayName": userData['displayName'],
            "email": userData['email'],
            "phoneNumber": userData['phoneNumber'],
            "dob": datetime.datetime(int(splittedDob[0]),int(splittedDob[1]),int(splittedDob[2])),
            "photoURL": userData['photoURL'],
            "gender": userData['gender'],
            "emailVerified": "boolean",
            "access": {"access":userData['access']},
            "status": {
                "isOnline": True,
                "access": 'active'
            },
            "state": userData['state'],
            "city": userData['city'],
            "pincode": userData['pincode'],
            "address": userData['address'],
            "aadhaarNumber": userData['aadhaarNumber'],
            "tutorialCompleted": False,
            "panCardNumber": userData['panNumber'],
            "qrCode": "",
            "onboardingDone": False,
            "payoutDetailsCompleted": False,
            "primaryPayoutAccount": None,
            "payoutFundAccount": [],
            "selfieImage": "",
            "shopImage": "",
            "memberAssigned": True,
            "kycStatus": 'incomplete',
            "onboardingSteps": {
                "phoneDobDone": False,
                "panDone": False,
                "locationDone": False,
                "aadhaarDone": False,
                "photosDone": False,
            },
            "messageToken": ""
        }
        if userData['access'] in self.accessLevels:
            user = self.firestore.collection(
                'users').document(userData['email'])
            doc = user.get()
            if doc.exists:
                return {'error': 'User already exists'}, 400
            else:
                user = self.auth.create_user(
                    email = userData['email'],
                    email_verified = False,
                    password = password,
                    display_name = userData['displayName'],
                    photo_url = userData['photoURL'],
                    disabled = False,
                    phone_number = '+91'+userData['phoneNumber']
                )
                data['userId'] = user.uid
                message = "Hi "+userData['displayName']+" . Welcome to SSSPay. You are Successfully Registered With Us. Your UserID is "+userData['email']+" and Password is "+password+".Please do not disclose your credentials to anyone. Regards SSSPAY"
                self.messaging.sendSingleSMS(message,userData['phoneNumber'])
                self.firestore.collection('users').document(data['userId']).set(data)
                return {'message': 'User created successfully',"response_code":1,"newUser":data}
        else:
            return {'error': 'Invalid access level requested'}, 400
