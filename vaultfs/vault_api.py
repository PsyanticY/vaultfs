from  vaultfs.logger import VaultfsLogger
#from  logger import VaultfsLogger
import argparse
import requests
import os.path
import json
import sys

# setting logger.
log = VaultfsLogger()

def check_remote(remote):
    try:
        r = requests.get(remote,timeout=5)
    except requests.exceptions.RequestException as e:
        log.error(e)
        sys.exit(1)

def check_folder(folder):
    if os.path.isdir(folder):
        return
    else:
        log.error("Failed to find '{}': No such directory".format(folder))
        sys.exit(1)

def check_file(file):
    if os.path.isfile(file):
        return
    else:
        log.error("Failed to find '{}': No such file".format(file))
        sys.exit(1)

def _auth_payload(payload):

    if os.path.isfile(payload):
        with open(payload) as f:
            auth_token = f.read()
        return auth_token.rstrip()
    else:
        log.error("Can't find the payload file containing the secret token")
        sys.exit(1) # This is not working properly
        # make sure we exit from fuse

# We needs to login as the role-id and get a token that we can use to get secrets
def get_secrets(payload, remote, secret_path, secret_name, full_path, data_key='content', timeout=1):

    # maybe an object for these remote, secret_path, secret_name
    headers = {"X-Vault-Token": _auth_payload(payload)}
    error_count = 0
    notFound = 0
    for i in range(0,len(secret_path)):
        remote_credentials_endpoint = remote + "/v1/" + secret_path[i] + "/data/" + secret_name
        try:
            r = requests.get(remote_credentials_endpoint, headers=headers, timeout=timeout)
            status = r.status_code
            reason = r.reason
            data = r.json()
        except requests.exceptions.RequestException as e:
            log.error(e.args[0])
            # get a better error message
            #sys.exit(1)
        # if status == 404:
        #     if 'errors' in data:
        #         error_count += 1
        if status == 200:
            credentials = data['data']['data'][data_key]
            with open(full_path, "w") as f:
                f.write(credentials)
            f.close()
            log.info("successfully got {} from vault".format(secret_name))
            break
        elif reason == "Forbidden":
            log.error("{}: {}".format(reason, data))
            # quit the loop since we can't authenticate to the server
            break
        elif reason == "NotFound":
            notFound += 1
        else:
            log.error("{}: {}".format(reason, data))
            break
    if (notFound == len(secret_path)):
        log.error("Can't find secret {} in provided secret engines: {} ".format(secret_name, ', '.join(self.secrets_path)))

def secrets_time(payload, remote, secret_path, secret_name, timeout=1):

    # maybe an object for these remote, secret_path, secret_name
    headers = {"X-Vault-Token": _auth_payload(payload)}
    exist = False
    for i in range(0,len(secret_path)):
        remote_credentials_endpoint = remote + "/v1/" + secret_path[i] + "/metadata/" + secret_name
        try:
            r = requests.get(remote_credentials_endpoint, headers=headers, timeout=timeout)
            status = r.status_code
            #reason = r.reason
            data = r.json()
        except requests.exceptions.RequestException as e:
            log.error(e.args[0])
            sys.exit(1)
        if status == 200:
            exist = True
            break
    if exist:
        current_version = data['data']['current_version']
        print(current_version)
        creation_time = data['data']['versions'][str(current_version)]['created_time']
        return creation_time.split(".", 1)[0]
    else:
        return None