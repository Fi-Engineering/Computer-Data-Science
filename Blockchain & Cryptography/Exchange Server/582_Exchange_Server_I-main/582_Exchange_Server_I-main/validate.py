#!/usr/bin/env python3

import random
import os
import sys
import subprocess

import eth_account
import algosdk
import requests
import json
import string
import signal

endpoint_url = "http://localhost"
endpoint_port = 5002

def is_port_in_use(port):
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


def validate():
    try:
        log = open( "server_log.txt", "a" )
    except Exception as e:
        print( e )
    already_running = False
    if is_port_in_use(endpoint_port):
        already_running = True
        print( "Flask server is already running" )
    else:
        print( "Starting Flask server" )
        try:
            flask_server = subprocess.Popen(["python3", "verification_endpoint.py"],
                                        stdout=log,
                                        stderr=log,
                                        shell=False,
                                        preexec_fn=os.setsid)
            #out, err = flask_server.communicate()
            #if err:
            #     print('The verification_endpoint raised an error:', err.decode())
            #else:
            #    print("Started Flask server!")
            try:
                outs, errs = flask_server.communicate(timeout=1)
                print( f"Errors = {errs}" )
            except subprocess.TimeoutExpired:
                pass
            except Exception as e:
                print( e )
            if flask_server.poll() is not None:
                print( "Error: Flask server stopped" )
        except Exception as e:
            print( e )
            print( "Failed" )
            return 0

    num_tests = 5
    num_passed = 0

    for _ in range(num_tests):
        try:
            num_passed += test_endpoint()
        except Exception as e:
            print( e )
            print( "test_endpoint() failed" )
            continue

    print( f"Passed {num_passed}/{4*num_tests} tests" )
    #Kill the server
    if not already_running:
        try:
            log.close()
            os.killpg(os.getpgid(flask_server.pid), signal.SIGTERM)
        except ProcessLookupError:
            pass
    return num_passed


def send_signed_msg(platform,msg,sk,pk,real=True):
    if platform == "Ethereum":
        msg_dict = {'message': msg, 'pk': pk, 'platform': platform }
        msg = json.dumps(msg_dict)
        eth_encoded_msg = eth_account.messages.encode_defunct(text=msg)
        eth_sig_obj = eth_account.Account.sign_message(eth_encoded_msg,sk)
        sig = eth_sig_obj.signature.hex()
    if platform == "Algorand":
        msg_dict = {'message': msg, 'pk': pk, 'platform': platform }
        msg = json.dumps(msg_dict)
        alg_encoded_msg = msg.encode('utf-8')
        sig = algo_sig_str = algosdk.util.sign_bytes(alg_encoded_msg,sk)

    if not real:
        msg_dict['message'] += "."
    post_dict = { 'sig': sig, 'payload': msg_dict }

    try:
        res = requests.get( f"{endpoint_url}:{endpoint_port}/verify", json=post_dict )
    except Exception as e:
        print( e )
        print( f"{endpoint_url}:{endpoint_port}/verify returns an error" )
        return None

    try:
        res_json = res.json()
    except Exception as e:
        print( e )
        print( f"{endpoint_url}:{endpoint_port}/verify did not return valid JSON" )
        print( f"Got: {res}" )
        return None
    return res_json

def test_endpoint():
    num_passed = 0
    for real in [True, False]:
        num_passed += test_Algo(real)
        num_passed += test_Eth(real)
    return num_passed

def test_Algo(real=True):
    algo_sk, algo_pk = algosdk.account.generate_account()
    platform = "Algorand"
    msg = ''.join(random.choice(string.ascii_letters) for i in range(20))

    response = send_signed_msg( platform, msg, algo_sk, algo_pk, real )
    if response != real:
        if real:
            print( "Error: failed to validate an Algorand signature" )
        else:
            print( "Error: validated an incorrect Algorand signature" )
    return response == real

def test_Eth(real=True):
    eth_account.Account.enable_unaudited_hdwallet_features()
    acct, mnemonic = eth_account.Account.create_with_mnemonic()

    eth_pk = acct.address
    eth_sk = acct.key
    platform = "Ethereum"
    letters = string.ascii_letters
    msg = ''.join(random.choice(string.ascii_letters) for i in range(20))

    response = send_signed_msg( platform, msg, eth_sk, eth_pk, real )
    if response != real:
        if real:
            print( "Error: failed to validate an Ethereum signature" )
        else:
            print( "Error: validated an incorrect Ethereum signature" )
    return response == real



