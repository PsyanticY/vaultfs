import argparse
import requests
import os.path
import json
import sys

def _auth_payload(payload):

    if os.path.isfile(payload):
        with open(payload) as f:
            auth_token = f.read()
            print (auth_token)
        return auth_token.rstrip()
    else:
        pass
        # implement those 2 functions
        #logger("Error: Payload do no exist")
        #error(exit)


# We needs to login as the role-id and get a token that we can use to get secrets
def get_secrets(payload, remote, secret_path, secret_name, data_key='content', timeout=1):

    # maybe an object for these remote, secret_path, secret_name
    headers = {"X-Vault-Token": _auth_payload(payload)}
    remote_credentials_endpoint = remote + "/v1/" + secret_path + "/data/" + secret_name
    try:
        r = requests.get(remote_credentials_endpoint, headers=headers, timeout=timeout)
        status = r.status_code
        reason = r.reason
        data = r.json()
    except requests.exceptions.RequestException as e:
        print(e.args[0])
        # get a better error message
        sys.exit(1)
    if status == 404:
        if 'errors' in data:
            #logger
            return ("Warning: Secret not Found in " + "'" + secret_path + "'" + " secret engine", "NotFound")
        #logger()
        if 'warnings' in data:
            print("Error: ", data['warnings'][0])
        # need to check for permissions stuff
    elif status == 200:
        credentials = data['data']['data'][data_key]
        return (credentials, "Success")
    else:
        print(data)
        return (data, reason)
        

    
