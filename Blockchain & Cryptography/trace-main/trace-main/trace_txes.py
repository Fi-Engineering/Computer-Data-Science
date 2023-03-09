from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
import json
from datetime import datetime

import requests

#import struct

rpc_user='quaker_quorum'
rpc_password='franklin_fought_for_continental_cash'
rpc_ip='3.134.159.30'
rpc_port='8332'

rpc_connection = AuthServiceProxy("http://%s:%s@%s:%s"%(rpc_user, rpc_password, rpc_ip, rpc_port))

###################################

class TXO:
    def __init__(self, tx_hash, n, amount, owner, time ):
        self.tx_hash = tx_hash 
        self.n = n
        self.amount = amount
        self.owner = owner
        self.time = time
        self.inputs = []

    def __str__(self, level=0):
        ret = "\t"*level+repr(self.tx_hash)+"\n"
        for tx in self.inputs:
            ret += tx.__str__(level+1)
        return ret

    def to_json(self):
        fields = ['tx_hash','n','amount','owner']
        json_dict = { field: self.__dict__[field] for field in fields }
        json_dict.update( {'time': datetime.timestamp(self.time) } )
        if len(self.inputs) > 0:
            for txo in self.inputs:
                json_dict.update( {'inputs': json.loads(txo.to_json()) } )
        return json.dumps(json_dict, sort_keys=True, indent=4)

    @classmethod
    def from_tx_hash(cls,tx_hash,n=0):
        #pass
        #YOUR CODE HERE
        tx = rpc_connection.getrawtransaction(tx_hash, True)
        txHash = tx["hash"]
        vin = tx["vin"]
        #print('vin: \n',vin , '\n')
        vinN = vin[0]["vout"]
        #print('vinN: ',vinN , '\n')
        vout = tx["vout"]
        #n = vout[1]['n']
        n = vinN
        value = vout[0]["value"]
        amount = int(float(value) * 1e8)
        owner = vout[0]["scriptPubKey"]["addresses"][0]
        time = tx["blocktime"]    
        time = datetime.fromtimestamp(time)
        # def __init__(self, tx_hash, n, amount, owner, time ):
        txoNew = TXO(txHash, n, amount, owner, time)
        #inputs = []
        return txoNew
        

    def get_inputs(self, d=1):
        #pass
        #YOUR CODE HERE
        resp = requests.get('https://blockchain.info/unspent?active=%s' % self.owner)
        utxo_list = json.loads(resp.text)["unspent_outputs"]
        self.inputs = utxo_list
        
    
