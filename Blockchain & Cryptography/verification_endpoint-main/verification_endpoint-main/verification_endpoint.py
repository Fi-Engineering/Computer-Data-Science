from flask import Flask, request, jsonify
from flask_restful import Api
import json
import eth_account
import algosdk

app = Flask(__name__)
api = Api(app)
app.url_map.strict_slashes = False

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    content = request.get_json(silent=True)
    msg = content['payload']['message']
    platform = content['payload']['platform']
    pyld = json.dumps(content['payload'])
    sig = content['sig']
    pk = content['payload']['pk'] 

    if(platform.upper() == 'ETHEREUM'):
        result = verify_eth(pyld, msg, pk, sig)

    elif(platform.upper() == 'ALGORAND'):
        result = verify_algorand(pyld, msg, pk, sig)

    return jsonify(result)
'''
import algosdk

payload = "Sign this!"

algo_sk, algo_pk = algosdk.account.generate_account()
algo_sig_str = algosdk.util.sign_bytes(payload.encode('utf-8'),algo_sk)

if algosdk.util.verify_bytes(payload.encode('utf-8'),algo_sig_str,algo_pk):
    print( "Algo sig verifies!" )
)
'''

def verify_algorand(pyld, msg, pk, sig):
    algo_sig_str = algosdk.util.sign_bytes(msg.encode('utf-8'), sig)
    if algosdk.util.verify_bytes(pyld.encode('utf-8'), sig, pk):
        result = True
    else:
        result = False
    return result

'''
import eth_account

eth_account.Account.enable_unaudited_hdwallet_features()
acct, mnemonic = eth_account.Account.create_with_mnemonic()

eth_pk = acct.address
eth_sk = acct.key

payload = "Sign this!"

eth_encoded_msg = eth_account.messages.encode_defunct(text=payload)
eth_sig_obj = eth_account.Account.sign_message(eth_encoded_msg,eth_sk)

print( eth_sig_obj.messageHash )
if eth_account.Account.recover_message(eth_encoded_msg,signature=eth_sig_obj.signature.hex()) == eth_pk:
    print( "Eth sig verifies!" )
'''
def verify_eth(pyld, msg, pk, sig):
    eth_encoded_msg = eth_account.messages.encode_defunct(text=pyld)
    if eth_account.Account.recover_message(eth_encoded_msg, signature=sig) == pk:
        result = True
    else:
        result = False
    return result

if __name__ == '__main__':
    app.run(port='5002')
