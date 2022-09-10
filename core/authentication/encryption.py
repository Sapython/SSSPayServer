from base64 import b64decode, b64encode
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
class Encrypt:
    def __init__(self):
        self.key = '519d2ac605e1b233'.encode('utf-8')
        self.iv = 'a3c63fe72e143786'.encode('utf-8')

    def encrypt(self,text:any):
        cipher = AES.new(self.key,AES.MODE_CBC,iv=self.iv)
        encryptedData = cipher.encrypt(pad(text,AES.block_size))
        return b64encode(encryptedData).decode('utf-8')

    def encodeHEX(self,message:str):
        return message.encode('hex')

    def decrypt(self, text:str):
        cipher = AES.new(self.key,AES.MODE_CBC,iv=self.iv)
        decoded = b64decode(text)
        return unpad(cipher.decrypt(decoded),AES.block_size)


if __name__ == "__main__":
    text = """{'latitude': ' 26.7484', 'longitude': '80.9335', 'mobilenumber': '9653901003', 'referenceno': '7686109653901003', 'ipaddress': '34.126.221.178', 'adhaarnumber': '787605281505', 'accessmodetype': 'SITE', 'nationalbankidentification': '508505', 'requestremarks': 'test', 'data': '<PidData>   <Resp errCode="0" errInfo="Success." fCount="1" fType="0" nmPoints="21" qScore="70" />   <DeviceInfo dpId="MANTRA.MSIPL" rdsId="MANTRA.WIN.001" rdsVer="1.0.4" mi="MFS100" mc="MIIEGDCCAwCgAwIBAgIEAIlUQDANBgkqhkiG9w0BAQsFADCB6jEqMCgGA1UEAxMhRFMgTWFudHJhIFNvZnRlY2ggSW5kaWEgUHZ0IEx0ZCA3MUMwQQYDVQQzEzpCIDIwMyBTaGFwYXRoIEhleGEgb3Bwb3NpdGUgR3VqYXJhdCBIaWdoIENvdXJ0IFMgRyBIaWdod2F5MRIwEAYDVQQJEwlBaG1lZGFiYWQxEDAOBgNVBAgTB0d1amFyYXQxHTAbBgNVBAsTFFRlY2huaWNhbCBEZXBhcnRtZW50MSUwIwYDVQQKExxNYW50cmEgU29mdGVjaCBJbmRpYSBQdnQgTHRkMQswCQYDVQQGEwJJTjAeFw0yMjA5MDEwMzIyMDlaFw0yMjEwMDEwMzM3MDlaMIGwMSUwIwYDVQQDExxNYW50cmEgU29mdGVjaCBJbmRpYSBQdnQgTHRkMR4wHAYDVQQLExVCaW9tZXRyaWMgTWFudWZhY3R1cmUxDjAMBgNVBAoTBU1TSVBMMRIwEAYDVQQHEwlBSE1FREFCQUQxEDAOBgNVBAgTB0dVSkFSQVQxCzAJBgNVBAYTAklOMSQwIgYJKoZIhvcNAQkBFhVzdXBwb3J0QG1hbnRyYXRlYy5jb20wggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQC3e4U8WB6YTaTArSAU65hBrIK+BEc9J95wi3jfmOraBlUp/FSd6Ov+6MzetggV6pBwfQRjVEFvpRz1iItHDC3orKhVerV2msNfb6Qotuh0hMmMn9eWTa8NpttPuN2CG/g830J0RvRmIvxywUa/NsjoR81GpUHZEvpyIrRh4MbVVi5HI4HnKN4nQ1D4yVXo/wY1TorO0YfADzABGV7IlZN8Nx878tJ1IBm+YzVGGqD6vKm6YQ9pfUXLfa9iVmClN7RNB7gSW+lhBBzronOPcj8raJHh25TSLU/Y50vOzAKcaKorBdVORlrlz5EudwiGhRABcNb+hUpOawB39quTtRfJAgMBAAEwDQYJKoZIhvcNAQELBQADggEBAKEat864LsP/k6W97Qds4rv/a7laf7Ilj6T5J3vo2/2tAk7H5DsrRmo3khc/SKBifwqPjaqbEK2n+SVhP0X5AaOcnjKdzV1i5THl1Dbtt36oPthQmxVt1qxSUfCQq6yFyIGupciqXSY3JGMXFLqtXE3QDLWz/D73p8dIq7+HKZVFBp4akkH60GfLA5YLTUUv22ei10o7xrGfAfbiyOTqXl5k4p9I7BXL3DdapxnAEE52rMjmEkSaYBuQapoXoRgAyRkK1shx5FI09R1bygKee+6krYB53Hpo40n85uI9OPK/pAyJ5wzpsP6+iSUx+YPDuX+hls+Af+cWlH6DARelDGs=" dc="d3484359-a7d8-4a9c-80ac-cf2194b6901c">     <additional_info>       <Param name="srno" value="5046779" />       <Param name="sysid" value="655FEBF3CA148FCFBFF0" />       <Param name="ts" value="2022-09-08T17:11:47+05:30" />     </additional_info>   </DeviceInfo>   <Skey ci="20221021">HA2fbUZj3hVmOM3g8w57GSKfzNcfgIHWfXQGWif1KOzZdgKTqTWvxubwS1aVb6vO3RGbSGfSd4tWUnZ9IF8QbncFeyqwdNQ/7M2OixquKVlQNQSfbOV0zuHI9L36bCWX09A+pXs+RjNCn1Z6OPK37dSWlOm1GmBh+K6EvfpUcoH7r8zlZ448NGNJBa7i+Gembex/UZEtajuRCOY9YhgxvVn39VQ0RW0QMS7vrp+WjkpYP6vyXDz0o8bJ9hX+KQHeUiC6gu4WJl6S3lerBfEw4S+dUjAKuMQV0hM+tRaF7UYJW1m1GD1PFXKOvZNMYlkDwRBq896ebxz/5zZufzoypA==</Skey>   <Hmac>hBYNkgrp/KY9w3L5omb7WxtM2H6lb5T0vNtLLQj7y+kpA0qx2SsDrAv4UTlDvrkr</Hmac>   <Data type="X">MjAyMi0wOS0wOFQxNzoxMTo0N0Ruo8bFemTrxtcahezZ3tEIAOrPpoYiVtvADQA1lIHHvK/UFcbhhSHvmfB4KnWEK+7caLVn6v8Lb8PsjQVxkFZm3FPUDSmXUsL2bh5pqGGZgDrV31HAHxnqH3lijAXvA4SN1nR65UCc/K/JsYzIFEQt+XIaDP8OLanJ5WY/YvAJMVeEZsOV830KAiVH7KUx0RSG1s2aUBoWXKikydY4v7tYLR8yEv+fUZuudYk4bzXg5+vL5ClLrrNNTqYXwN4Tq2rG2NgmDJylReKSXR3lkOLHK2N4yHjddL9TPXP6KCYqLM1YMf6ZKGYrXov5/Rh+3sLPSquL6KvsrC5bdjhD7JhujYqQpH2NlYm5OUl0vZTLDFrVN3tAIlhrO11m/4AjGykzXUh7QwQEEB/EV3vvMVdNxsxK2HnHNXG31UBr8ubN+Hxs9o9Eh8ZQs88B1rmF9JzFjn21y0E7WDXWdVzcJomShOdFirMAJKL8N1UL7vko3rm5tx1Ovm2SrKJOtgN9LZOSVeBqelzvBLpQjNPK5OyfwiLdZz7fGplfjh4rqn3z+1eYvMy01lIshNGzb2kbkzAs1YfQQBR6mHCO+1Onetr0rq2f7itdHHfB2EVL2sLhFKsP/Xjd2k4g2HTL+D3+zPmPtjCz/38asUrW37IBGzCLkfdW4Lx/18I9EBJnpa2k2PvJ5TKbc+ox+HbgOucOHfyD+a8oCKeC9v+AFet9Niuw2LzYDgKhpG+avikiuA8ylGxzzpLjrnIiVXX8uFh2xKhWU4qcUHT9b8SLTY+F2samphK2OXwN8tUnwI0xB4J5eKJcEerPHcpNr2cKtRUVETt0unt6fYzmaLzXl2ImN1AZETPem3PIJUhznQ2fFsQU4e9jqCj8MOL0QAZV/KRZAfGYn8dn+zuMBraDvhyxfPiEeuwgWdpCTOtKnK3YUy1eZezNQ0lgK+TyIv1qCT27yGIomlw3pdLKL5glmwU7MhPb1qh/OcRp2LX8B8VH8/xBLi9NVA==</Data> </PidData>', 'pipe': 'bank1', 'timestamp': '2022-09-08 18:33:44', 'transactiontype': 'BE', 'submerchantid': 'bwYXqVOM8YdxzDk9ltxY7TAiBId2', 'is_iris': False}"""
    for i in range(5):
        e = Encrypt()
        encrypted = e.encrypt(text.encode())
        decrypted = e.decrypt(encrypted)
        print(encrypted)
        print(decrypted)
        if decrypted != text.encode():
            print("Unmatched",text)
