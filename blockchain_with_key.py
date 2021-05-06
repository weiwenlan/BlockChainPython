import hashlib
from os import error
import time
import json
from Crypto import Signature
from Crypto import PublicKey
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.Signature import PKCS1_v1_5 as Signature_pkcs1_v1_5
from Crypto.Hash import SHA
import base64
from encryp_RSA import RSA_mKey_Sign, RSA_mKey_CheckSign
encode_gbk_utf8 = 'utf-8'

class Transaction():
    def __init__(self,address_from,address_to,amount) -> None:
        self.add_to = address_to
        self.add_from = address_from
        self.amount = amount
        self.signature = ''
        # use private key to sign
        # use public key to valid the data, there the public key is read from the file,
        # in the real situation, address_from provide this public key
        

    def return_value(self):
        return {'from':self.add_from,'to':self.add_to,'amount':self.amount}

    def calculate_hash(self) -> str:
        raw_str =self.add_from + self.add_to + str(self.amount) 
        sha256 = hashlib.sha256()
        sha256.update(raw_str.encode('utf-8'))
        hash = sha256.hexdigest()
        return hash

    def sign(self,key):
        rsakey = RSA.importKey(key) 
        signer = Signature_pkcs1_v1_5.new(rsakey)
        message =str(self.add_from) + str(self.add_to) + str(self.amount) 
        digest = SHA.new() 
        digest.update(message.encode(encoding='utf-8')) 
        sign = signer.sign(digest) 
        signature = base64.b64encode(sign)  
        self.signature = signature
    
    def isValid(self):
        if self.add_from =='':
            return True
        if self.signature =='':
            raise error('unsigned')
        publickey = self.add_from
        rsakey = RSA.importKey(publickey) 
        verifier = Signature_pkcs1_v1_5.new(rsakey) 
        message =str(self.add_from) + str(self.add_to) + str(self.amount) 
        digest = SHA.new()
        # 注意内容编码和base64解码问题 
        digest.update(message.encode(encoding='utf-8')) 
        is_verify = verifier.verify(digest, base64.b64decode(self.signature)) 
        return is_verify








class Block():
    def __init__(self,data,timestamp,previous_hash='') -> None:
        self.data = data
        self.pre_hash =previous_hash
        self.nonce = 0
        self.timestamp = timestamp

        self.hash = self.calculate_hash()
       

    def calculate_hash(self) -> str:

        raw_str = str(self.data) + self.pre_hash + str(self.nonce) + str(self.timestamp)
        #raw_str = str(self.data[0].add_to)+str(self.data[0].add_from) + str(self.data[0].amount) + self.pre_hash + str(self.nonce) + str(self.timestamp)
        sha256 = hashlib.sha256()
        sha256.update(raw_str.encode('utf-8'))
        hash = sha256.hexdigest()
        return hash

    def mine_block(self, difficulty):
        '''
        how mine works
        :param difficulty: how many 0 in the row
        :return:
        '''
        while self.hash[0: difficulty] != ''.join(['0'] * difficulty):
            self.nonce += 1
            self.hash = self.calculate_hash()
        print("mine block:%s, in: %f sec" % (self.hash, time.process_time()))

    def blockValidation(self):
        for i in self.data:
            if not i.isValid():
                return False
        return True


class Chain():
    def __init__(self) -> None:
        self.chain = [self.GenesisBlock()]
        self.difficulty = 2
        self.transactionPool =[]
        self.minerReward = 50
    
    
    def GenesisBlock(self):
        return Block('Genesis',time.time(),'')
    
    def GetLatestBlcok(self):
        return self.chain[-1]

    def AddBlock(self,newBlock):
        newBlock.timestamp=time.time()
        newBlock.pre_hash = self.GetLatestBlcok().hash
        newBlock.mine_block(self.difficulty)
        self.chain.append(newBlock)


    def addTran(self,transaction):
        if (not transaction.isValid()):
            raise error('Block inValid')
        
        self.transactionPool.append(transaction)

    def mineTranPool(self,minerAddress):
        '''
        这里忽略每个block挖出之后根据Transaction，miner能获得一定的转账费
        '''
        if not self.verify_chain():
            raise error('Chain changed')
        MinerRewardTransaction = Transaction('',minerAddress,self.minerReward)
        self.transactionPool.append(MinerRewardTransaction)
        mineBlock = Block(self.transactionPool,time.time(),self.GetLatestBlcok().hash)
        mineBlock.mine_block(self.difficulty)
        mineBlock.pre_hash = self.GetLatestBlcok().hash

        self.chain.append(mineBlock)
        self.transactionPool = []
    
    def verify_block(self,block):
        '''
        verify the integerity of the single Block
        :return bool
        '''
        if block.hash == block.calculate_hash():
            return True
        else:
            return False



    def verify_chain(self):
        '''
        verify the integerity of the chain
        :return: bool
        '''
        if len(self.chain)==1:
            return self.verify_block(self.chain[0])
        else:
            for i in range(1, len(self.chain)):
                current_block = self.chain[i]
                if not current_block.blockValidation():
                    return False
                previous_block = self.chain[i - 1]  
                if current_block.hash != current_block.calculate_hash():
                    print(current_block.hash)
                    print(current_block.calculate_hash())
                    print('data changed')
                    return False
                if current_block.pre_hash != previous_block.calculate_hash():
                    print('chain changed')
                    return False
            return True
    


def checkBlock(Block):
    print('data:    ',Block.data)
    print('hash:    ',Block.hash)
    print('pre_hash:',Block.pre_hash)
    print('')

    

wenlanCoin = Chain()

rsa = RSA.generate(1024)
privatekeySender = rsa.exportKey()
publicpemSender = rsa.publickey().exportKey()

rsa = RSA.generate(1024)
privatepemReceiver = rsa.exportKey()
publicpemReceiver = rsa.publickey().exportKey()

t1=Transaction(publicpemSender,publicpemReceiver,'10')
t1.sign(privatekeySender)
wenlanCoin.addTran(t1)
wenlanCoin.mineTranPool(publicpemReceiver)

t2=Transaction(publicpemReceiver,publicpemSender,'10')
t2.sign(privatepemReceiver)
wenlanCoin.addTran(t2)
wenlanCoin.mineTranPool(publicpemSender)


for i in wenlanCoin.chain:
    checkBlock(i)
# t2=Transaction('addr2','addr1','5')

# wenlanCoin.addTran(t2)

# wenlanCoin.mineTranPool('addr3')
# for i in wenlanCoin.chain:
#     checkBlock(i)
# print(wenlanCoin.chain[-1].data)



# wenlanChain = Chain()
# wenlanChain.difficulty = 3
# block1=Block('Transfer 10','')
# wenlanChain.AddBlock(block1)
# block1=Block('Transfer 20','')
# wenlanChain.AddBlock(block1)
# block1=Block('Transfer 30','')
# wenlanChain.AddBlock(block1)


# print('*********',wenlanChain.verify_chain(),'*********')
# for i in wenlanChain.chain:
#     checkBlock(i)

# # change the block 
# wenlanChain.chain[2].data='996'

# print('*********',wenlanChain.verify_chain(),'*********')
# for i in wenlanChain.chain:
#     checkBlock(i)



