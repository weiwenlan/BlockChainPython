import hashlib

def jm_sha256(key, value):
    """
    sha256加密
    :param key:
    :param value: 加密字符串
    :return: 加密结果转换为16进制字符串，并大写
    """
    hsobj = hashlib.sha256(key.encode("utf-8"))
    hsobj.update(value.encode("utf-8"))
    return hsobj.hexdigest()

def proof_of_work():
    y = 'wenlan'
    x = 0

    while(True):
        z = y+str(x)
        val=jm_sha256("name",str(z))
        if val[0]=='0':
            return x,val
        else:
            x = x+1
    


print("sha256加密：", jm_sha256("name", "WenlanWei"))
print(proof_of_work())
