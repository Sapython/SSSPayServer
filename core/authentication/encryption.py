from Crypto.Cipher import AES
class Encrypt:
    def __init__(self):
        self.key = '519d2ac605e1b233'.encode('utf-8')
        self.iv = 'a3c63fe72e143786'.encode('utf-8')
        self.cipher = AES.new(self.key,AES.MODE_CBC,iv=self.iv)

    def encrypt(self,text:any):
        length = 16 - (len(text) % 16)
        print(length)
        text += bytes([length])*length
        print(text)
        return self.cipher.encrypt(text)

    def encodeHEX(self,message:str):
        return message.encode('hex')

    def decrypt(self, text:str):
        return self.cipher.decrypt(text)