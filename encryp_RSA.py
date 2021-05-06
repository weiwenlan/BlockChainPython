from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.Signature import PKCS1_v1_5 as Signature_pkcs1_v1_5
from Crypto.Hash import SHA
import hashlib
import base64

encode_gbk_utf8 = 'utf-8'


# RSA的公私钥生成
def RSA_Create_Key(): 
    # random_generator = random.new().read  # 伪随机数生成器 
    rsa = RSA.generate(1024)  
    # rsa算法生成实例 
    private_pem = rsa.exportKey()  
    # master的秘钥对的生成 # 生成公私钥对文件 
    with open('master-private.pem', 'wb') as f: 
        f.write(private_pem) 
    public_pem = rsa.publickey().exportKey() 
    with open('master-public.pem', 'wb') as f: 
        f.write(public_pem) 
    # ghost的秘钥对的生成,与master内容一样，如果想不一样请重新生成rsa实例 
    private_pem = rsa.exportKey() 
    with open('ghost-private.pem', 'wb') as f: 
        f.write(private_pem) 
    public_pem = rsa.publickey().exportKey() 
    with open('ghost-public.pem', 'wb') as f: 
        f.write(public_pem)


# ghost使用公钥加密
def RSA_gKey_Encrypt(message): 
    with open('ghost-public.pem', 'rb') as f: 
        key = f.read() 
    rsakey = RSA.importKey(key)  
    # 导入读取到的公钥 
    cipher = Cipher_pkcs1_v1_5.new(rsakey)  
    # 生成对象 
    # 加密message明文，python3加密的数据必须是bytes，不能是str 
    cipher_text = base64.b64encode(cipher.encrypt( message.encode(encoding=encode_gbk_utf8))) 
    return cipher_text


# ghost使用私钥解密
def RSA_gKey_Decrypt(cipher_text): 
    with open('ghost-private.pem', 'rb') as f: 
        key = f.read() 
    rsakey = RSA.importKey(key)  
    # 导入读取到的私钥 
    cipher = Cipher_pkcs1_v1_5.new(rsakey)  
    # 生成对象 
    # 将密文解密成明文，返回的是bytes类型，需要自己转成str,主要是对中文的处理 
    text = cipher.decrypt(base64.b64decode(cipher_text), "ERROR") 
    return text.decode(encoding=encode_gbk_utf8)


# master 使用私钥对内容进行签名
def RSA_mKey_Sign(message): 
    with open('master-private.pem', 'rb') as f: 
        key = f.read() 
    rsakey = RSA.importKey(key) 
    signer = Signature_pkcs1_v1_5.new(rsakey) 
    digest = SHA.new() 
    digest.update(message.encode(encoding=encode_gbk_utf8)) 
    sign = signer.sign(digest) 
    signature = base64.b64encode(sign)  
    # 对结果进行base64编码 
    return signature


# master 使用公钥对内容进行验签
def RSA_mKey_CheckSign(message, signature): 
    with open('master-public.pem', 'rb') as f: 
        key = f.read() 
    rsakey = RSA.importKey(key) 
    verifier = Signature_pkcs1_v1_5.new(rsakey) 
    digest = SHA.new()
    # 注意内容编码和base64解码问题 
    digest.update(message.encode(encoding=encode_gbk_utf8)) 
    is_verify = verifier.verify(digest, base64.b64decode(signature)) 
    return is_verify



if __name__ == "__main__": 
    '''
    # 如果要加密的内容是超长字符串或大文件，直接for一下进行分块操作就行
    try: 
        with open('test_100MB.txt','rb') as f: 
            while True: message = f.read(64) 
            #长度由证书位数决定 #rsa操作代码 
    except EOFError:
        pass 
    ''' 
        
    message = 'hello world, 你好世界 !' 
    RSA_Create_Key() 
    try: 
        # ghost使用公钥加密
        cipher_text = RSA_gKey_Encrypt(message) 
        print(cipher_text) 
        # ghost使用私钥解密
        text = RSA_gKey_Decrypt(cipher_text) 
        print(text) 
        # master 使用私钥对内容进行签名
        signature = RSA_mKey_Sign(message) 
        print(signature) 
        # master 使用公钥对内容进行验签
        is_verify = RSA_mKey_CheckSign(message, signature) 
        print(is_verify) 
    except: 
        print('rsa run error')