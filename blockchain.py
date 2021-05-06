import hashlib
import time
import json

class Transaction():
    def __init__(self,address_to,address_from,amount) -> None:
        self.add_to = address_to
        self.add_from = address_from
        self.amount = amount


    def return_value(self):
        return {'from':self.add_from,'to':self.add_to,'amount':self.amount}



class Block():
    def __init__(self,data,timestamp,previous_hash='') -> None:
        self.data = str(data)
        self.pre_hash =previous_hash
        self.nonce = 0
        self.timestamp = timestamp

        self.hash = self.calculate_hash()
       

    def calculate_hash(self) -> str:

        # raw_str = self.previous_hash + str(self.timestamp) + json.dumps(self.data, ensure_ascii=False)
        raw_str =self.data + self.pre_hash + str(self.nonce) + str(self.timestamp)
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
        self.transactionPool.append(transaction.return_value())

    def mineTranPool(self,minerAddress):
        '''
        这里忽略每个block挖出之后根据Transaction，miner能获得一定的转账费
        '''
        MinerRewardTransaction = Transaction('',minerAddress,self.minerReward)
        self.transactionPool.append(MinerRewardTransaction)
        mineBlock = Block(self.transactionPool,self.GetLatestBlcok().hash)
        mineBlock.mine_block(self.difficulty)
        mineBlock.pre_hash = self.GetLatestBlcok().hash

        self.chain.append(mineBlock)
        self.transactionPool = []
    
    def verify_block(self):
        '''
        verify the integerity of the single Block
        :return bool
        '''
        if Block.hash == Block.calculate_hash():
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
                previous_block = self.chain[i - 1]  
                if current_block.hash != current_block.calculate_hash():
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
t1=Transaction('addr1','addr2','10')
t2=Transaction('addr2','addr1','5')
wenlanCoin.addTran(t1)
wenlanCoin.addTran(t2)

wenlanCoin.mineTranPool('addr3')
for i in wenlanCoin.chain:
    checkBlock(i)
print(wenlanCoin.chain[-1].data)



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



