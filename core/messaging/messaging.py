import requests
import re
import urllib
class Messaging:
    def __init__(self):
        """
        The function __init__() is a special method, called as class constructor or initialization
        method that Python calls when you create a new instance of this class
        """
        self.user = 'Sethsumit31'
        self.password = 'Sbi@123'
        self.senderId = 'SSSPAY'
    
    def sendSingleSMS(self,message:str,mobileNo:int,priority='ndnd'):
        """
        It sends a single SMS to a single mobile number
        
        :param message: The message you want to send
        :type message: str
        :param mobileNo: The mobile number to which the SMS is to be sent
        :type mobileNo: int
        :param priority: ndnd or dnd, defaults to ndnd (optional)
        :return: The response object
        """
        # encode message to url format
        print("before",message)
        message = urllib.parse.quote(message)
        print("after",message)
        smsType = 'normal'
        templateId = "1207162099029436668"
        dltId = '1201161855222539289'
        if (len(str(mobileNo))!=10):
            raise Exception('Invalid Mobile Number')
            return
            # http://nimbusit.biz/api/SmsApi/SendSingleApi?UserID=#USSERID#&Password=#Password#&SenderID=#SENDERID#&Phno=#PHONE#&Msg=#MSG#&EntityID=#EntityID#&TemplateID=#TEMPLATEID#
        print(f'http://nimbusit.biz/api/SmsApi/SendSingleApi?UserID={self.user}&Password={self.password}&SenderID={self.senderId}&Phno={str(mobileNo)}&Msg={message}&EntityID={dltId}')
        return requests.get(f'http://nimbusit.biz/api/SmsApi/SendSingleApi?UserID={self.user}&Password={self.password}&SenderID={self.senderId}&Phno={str(mobileNo)}&Msg={message}&EntityID={dltId}&TemplateId={templateId}')
    
    def sendOtp(self,otp,mobile):
        dltId = '1201161855222539289'
        message = ("{otp} is your OTP for Login. OTP valid for {mobile} minutes. Regards SSSPAY").format(otp=otp,mobile=mobile)
        return requests.get(f'http://nimbusit.biz/api/SmsApi/SendSingleApi?UserID={self.user}&Password={self.password}&SenderID={self.senderId}&Phno={str(mobile)}&Msg={message}&EntityID={dltId}&TemplateId=1207161883476515597')
    
    def sendMultiSMS(self,message:str,mobileNos:list,priority="dnd"):
        """
        It sends a single SMS to a single mobile number
        
        :param message: The message you want to send
        :type message: str
        :param mobileNos: A list of mobile numbers to which the SMS is to be sent
        :type mobileNos: list[int]
        :param priority: dnd or normal, defaults to dnd (optional)
        :return: A response object.
        """
        # A function that sends a single SMS to a single mobile number.
        smsType = 'normal'
        for number in mobileNos:
            if (len(number)!=10):
                raise Exception('Invalid Mobile Number')
                return
        if (len(mobileNos)>0):
            raise Exception('No Receiver Mobile No Given')
            return
        elif (len(message)>260):
            raise Exception('Message is tz  oo long')
            return
        elif (priority !='ndnd' or priority != 'dnd'):
            raise Exception('Not a valid priority')
            return
        elif (smsType !='normal' or smsType != 'flash'):
            raise Exception('Not a valid sms type')
            return
        return requests.get(f'http://trans.smsfresh.co/api/sendmsg.php?user={self.user}&pass={self.password}&sender={self.senderId}&phone={mobileNos}&text={message}&priority={priority}&stype=normal')
    
    def scheduleSMS(self,message:str,mobileNos:int,time:str,priority='dnd'):
        """
        It schedules a message to be sent at a particular time
        
        :param message: The message to be sent
        :type message: str
        :param mobileNos: A list of mobile numbers to which the message is to be sent
        :type mobileNos: int
        :param time: The time at which the message is to be sent
        :type time: str
        :param priority: dnd or ndnd, defaults to dnd (optional)
        :return: A response object.
        """
        # A function that schedules a message to be sent at a particular time.
        smsType = 'normal'
        timeRegex = re.search(r'\d{4}-\d{2}-\d{2} ([0-1]?[0-9]|2[0-3]):[0-5][0-9]', time)
        for number in mobileNos:
            if (len(number)!=10):
                raise Exception('Invalid Mobile Number')
                return
        if (len(mobileNos)>0):
            raise Exception('No Receiver Mobile No Given')
            return
        elif (len(message)>260):
            raise Exception('Message is tz  oo long')
            return
        elif (priority !='ndnd' or priority != 'dnd'):
            raise Exception('Not a valid priority')
            return
        elif (smsType !='normal' or smsType != 'flash'):
            raise Exception('Not a valid sms type')
            return
        elif (timeRegex == None):
            raise Exception('Not a valid time it should be in DD:MM:YYYY HH:MM format')
            return
        time = re.search(r'\d{4}-\d{2}-\d{2} ([0-1]?[0-9]|2[0-3]):[0-5][0-9]', time)
        return requests.get(f'http://trans.smsfresh.co/api/schedulemsg.php?user={self.user}&pass={self.password}&sender={self.senderId}&phone={mobileNos}&text={message}&priority={priority}&stype=normal&time={time}')

    def getBalance(self) -> int:
        """
        It returns the balance of the account.
        :return: The balance of the account.
        """
        # Getting the balance of the account.
        response = requests.get(f'http://trans.smsfresh.co/api/checkbalance.php?user={self.user}&pass={self.password}')
        return int(response.text)

    def getSenderId(self) -> str:
        """
        It returns the sender id of the account
        :return: The sender id of the account.
        """
        # Getting the sender id of the account.
        response = requests.get(f'http://trans.smsfresh.co/api/getsenderids.php?user={self.user}&pass={self.password}')
        return response.text
    
    def addSenderId(self,smsType='dnd') -> str:
        """
        This function adds a sender id to the account
        
        :param smsType: dnd or normal, defaults to dnd (optional)
        :return: The response text is being returned.
        """
        # Adding a sender id to the account.
        response =requests.get(f'http://trans.smsfresh.co/api/addsenderid.php?user={self.user}&senderid=SENDER&type={smsType}')
        return response.text
    
    

        

        

