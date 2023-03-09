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

    # store the platform as a separate variable from the json
    platform = content['payload']['platform']

    # store the variables
    payload = json.dumps(content['payload'])
    msg = content['payload']['message']
    pk = content['payload']['pk']
    sig = content['sig']

    result = False

    if(platform.upper() == 'ETHEREUM'):
        result = verify_eth(payload, msg, pk, sig)

    elif(platform.upper() == 'ALGORAND'):
        result = verify_algorand(payload, msg, pk, sig)

    return jsonify(result)

def verify_eth(payload, msg, pk, sig):
    eth_encoded_msg = eth_account.messages.encode_defunct(text=payload)
    result = False
    if eth_account.Account.recover_message(eth_encoded_msg, signature=sig) == pk:
        result = True
    else:
        result = False
    return result

def verify_algorand(payload, msg, pk, sig):
    algo_sig_str = algosdk.util.sign_bytes(msg.encode('utf-8'), sig)

    result = False;
    if algosdk.util.verify_bytes(payload.encode('utf-8'), sig, pk):
        result = True
    else:
        result = False
    return result

if __name__ == '__main__':
    app.run(port='5002')
