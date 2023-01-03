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
        self.accessLevels = ['guest', 'blocked', 'retailer', 'distributor',
                             'masterDistributor', 'superDistributor', 'admin']

    def getUserByPhone(self, phone):
        user = self.auth.get_user_by_phone_number(phone)
        if (user):
            return {"status": "success", "userId": user.uid}
        else:
            return {"error": "User does not exist"}

    def getUserByEmail(self, email):
        user = self.auth.get_user_by_email(email)
        if (user):
            return {"status": "success", "userId": user.uid}
        else:
            return {"error": "User does not exist"}

    def resetPassword(self, userId, password):
        self.auth.update_user(userId, password=password)
        return {'message': 'Password reset successfully'}

    def unblockUser(self, userId, blockedId):
        if not (userId and blockedId):
            return {'error': 'Missing parameters'}, 400
        user = self.firestore.collection('users').document(userId)
        doc = user.get()
        if doc.exists:
            data = doc.to_dict()
            if data['access']['access'] in ['admin']:
                self.firestore.collection('users').document(
                    blockedId).update({'status': {'access': 'active'}, 'access': {'access': 'guest'}})
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
                docRef.update({'status': {'access': 'blocked'},
                              'access': {'access': 'blocked'}})
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
        password = ''.join(random.choices(
            string.ascii_letters + string.digits, k=6))
        splittedDob = userData['dob'].split('-')
        data = {
            "displayName": userData['displayName'],
            "email": userData['email'],
            "phoneNumber": userData['phoneNumber'],
            "dob": datetime.datetime(int(splittedDob[0]), int(splittedDob[1]), int(splittedDob[2])),
            "photoURL": userData['photoURL'],
            "gender": userData['gender'],
            "emailVerified": "boolean",
            "access": {"access": userData['access']},
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
        try:
            user = self.auth.get_user_by_email(userData['email'])
        except:
            print("User does not exist")
            user = None
        userData['uid'] = user.uid if user else 'nouser'
        print("User data",userData["uid"])
        if userData['access'] in self.accessLevels:
            user = self.firestore.collection(
                'users').document(userData['uid'])
            doc = user.get()
            uidNumber = self.firestore.collection('uidCounter').document('counter').get().to_dict()['counter']
            # 'admin'
            # 'superDistributor',
            # 'masterDistributor',
            # 'distributor',
            # 'retailer',
            # 'guest',
            accessShortCode = ""
            if userData['access'] == 'admin':
                accessShortCode = 'ADM'
            elif userData['access'] == 'superDistributor':
                accessShortCode = 'SD'
            elif userData['access'] == 'masterDistributor':
                accessShortCode = 'MD'
            elif userData['access'] == 'distributor':
                accessShortCode = 'D'
            elif userData['access'] == 'retailer':
                accessShortCode = 'R'
            elif userData['access'] == 'guest':
                accessShortCode = 'G'
            uid = 'SSSPAY'+accessShortCode+str(uidNumber)
            if doc!=None and doc.exists:
                return {'error': 'User already exists'}, 400
            else:
                user = self.auth.create_user(
                    uid=uid,
                    email=userData['email'],
                    email_verified=False,
                    password=password,
                    display_name=userData['displayName'],
                    photo_url=userData['photoURL'],
                    disabled=False,
                    phone_number='+91'+userData['phoneNumber']
                )
                self.firestore.collection('uidCounter').document('counter').update({'counter': firestore.Increment(1)})
                data['userId'] = user.uid
                # message = "Hi "+userData['displayName']+" . Welcome to SSSPay. You are Successfully Registered With Us. Your UserID is "+userData['email']+" and Password is "+password+".Please do not disclose your credentials to anyone. Regards SSSPAY"
                message = ("Successfully Registered With SSSPay.Your UserID is {name} and Password is {password} do not disclose to anyone").format(
                    name=userData['email'], password=password)
                self.messaging.sendSingleSMS(message, userData['phoneNumber'])
                self.firestore.collection('users').document(
                    data['userId']).set(data)
                return {'message': 'User created successfully', "response_code": 1, "newUser": data}
        else:
            return {'error': 'Invalid access level requested'}, 400

    def testFunction(self):
        # userData = {
        #     "uid": "P4JHNdQLacXaSd8RFN61XUQ7A22",
        #     "displayName": "Hariom Kushawaha",
        #     "email": "hariomkushwaha8423@gmail.com",
        #     "phoneNumber": "8423522492",
        #     "dob": "1999-01-01",
        #     "password":"ifZp8w",
        #     "photoURL": "https://firebasestorage.googleapis.com/v0/b/sit-manager.appspot.com/o/users%2Fdefault%2Fuser.png?alt=media&token=f7502ba7-275f-40a8-92bd-7df725bc7786",
        #     "gender":"male",
        #     "access": "guest",
        #     "state": "Uttar Pradesh",
        #     "city": "",
        #     "pincode": "",
        #     "address": "",
        #     "aadhaarNumber": "",
        #     "panNumber": ""
        # }
        # splittedDob = userData['dob'].split('-')
        # data = {
        #     "displayName": userData['displayName'],
        #     "email": userData['email'],
        #     "phoneNumber": userData['phoneNumber'],
        #     "dob": datetime.datetime(int(splittedDob[0]), int(splittedDob[1]), int(splittedDob[2])),
        #     "photoURL": userData['photoURL'],
        #     "gender": userData['gender'],
        #     "emailVerified": "boolean",
        #     "access": {"access": userData['access']},
        #     "status": {
        #         "isOnline": True,
        #         "access": 'active'
        #     },
        #     "state": userData['state'],
        #     "city": userData['city'],
        #     "pincode": userData['pincode'],
        #     "address": userData['address'],
        #     "aadhaarNumber": userData['aadhaarNumber'],
        #     "tutorialCompleted": False,
        #     "panCardNumber": userData['panNumber'],
        #     "qrCode": "",
        #     "onboardingDone": False,
        #     "payoutDetailsCompleted": False,
        #     "primaryPayoutAccount": None,
        #     "payoutFundAccount": [],
        #     "selfieImage": "",
        #     "shopImage": "",
        #     "memberAssigned": True,
        #     "kycStatus": 'incomplete',
        #     "onboardingSteps": {
        #         "phoneDobDone": False,
        #         "panDone": False,
        #         "locationDone": False,
        #         "aadhaarDone": False,
        #         "photosDone": False,
        #     },
        #     "messageToken": ""
        # }
        # user = self.auth.create_user(
        #     uid=userData['uid'],
        #     phone_number= "+91"+userData['phoneNumber'] ,
        #     email= userData['email'],
        #     email_verified=True,
        #     password=userData['password'],
        #     display_name=userData['displayName'],
        #     photo_url=userData["photoURL"],
        #     disabled=False
        # )
        user = self.auth.update_user(
            uid="YpBrnCoe4laoeY1RmTCZ4pupOys2",
            password= "Sirsa@12345"
        )
        # # return "Done"
        # data['userId'] = user.uid
        # # message = "Hi "+userData['displayName']+" . Welcome to SSSPay. You are Successfully Registered With Us. Your UserID is "+userData['email']+" and Password is "+password+".Please do not disclose your credentials to anyone. Regards SSSPAY"
        # # message = ("Successfully Registered With SSSPay.Your UserID is {name} and Password is {password} do not disclose to anyone").format(
        # #     name=userData['email'], password=password)
        # # self.messaging.sendSingleSMS(message, userData['phoneNumber'])
        # self.firestore.collection('users').document(data['userId']).set(data)
        return "Done"
