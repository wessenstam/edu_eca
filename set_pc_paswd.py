# This script is to deploy the HPOC clusters for the vECA training
# 30-04-2020: Willem Essenstam - Initial version 0.1
# Order:
# 1. Accept EULA
# 2. Disable Pulse
# 3. Upload images

import requests
import json
import urllib3
import sys

#####################################################################################################################################################################
# This function is to get the to see if the initialisation of the cluster has been run (EULA, PULSE, Network)
#####################################################################################################################################################################
def get_json_data(ip_address, get_url, json_data, method, user, passwd, value):
    # Get the URL and compose the command to get the request from the REST API of the cluster
    url = "https://" + ip_address + ":9440/" + get_url
    header_post = {'Content-type': 'application/json'}
    # if method is not set assume GET
    if method == "":
        method = "get"

    # Set the right requests based on GET or POST
    if method.lower() == "get":
        try:
            page = requests.get(url, verify=False, auth=(user, passwd), timeout=15)
            page.raise_for_status()
            json_data = json.loads(page.text)
            return json_data
        except requests.exceptions.RequestException as err:
            print("OOps Error: Something Else", err)
            return err
        except requests.exceptions.HTTPError as errh:
            print("Http Error:", errh)
        except requests.exceptions.ConnectionError as errc:
            print("Error Connecting:", errc)
        except requests.exceptions.Timeout as errt:
            print("Timeout Error:", errt)

    elif method.lower() == "post":
        try:
            page = requests.post(url, verify=False, auth=(user, passwd), data=json_data, headers=header_post,
                                 timeout=15)
            page.raise_for_status()
            json_data = json.loads(page.text)
            return json_data
        except requests.exceptions.RequestException as err:
            print("OOps: Something Else", err)
        except requests.exceptions.HTTPError as errh:
            print("Http Error:", errh)
        except requests.exceptions.ConnectionError as errc:
            print("Error Connecting:", errc)
        except requests.exceptions.Timeout as errt:
            print("Timeout Error:", errt)

    else:
        try:
            page = requests.put(url, verify=False, auth=(user, passwd), data=json_data, headers=header_post, timeout=15)
            page.raise_for_status()
            json_data = json.loads(page.text)
            return json_data
        except requests.exceptions.RequestException as err:
            print("OOps: Something Else", err)
        except requests.exceptions.HTTPError as errh:
            print("Http Error:", errh)
        except requests.exceptions.ConnectionError as errc:
            print("Error Connecting:", errc)
        except requests.exceptions.Timeout as errt:
            print("Timeout Error:", errt)


#####################################################################################################################################################################
# __main__
#####################################################################################################################################################################
# Take the SSL warning out of the screen
urllib3.disable_warnings()

# Fill the array with the IP addrresses
# Use a file with parameters to run the checks
file=open("cluster.txt","r")
file_line=file.readlines()
server_run_list=[]
for line in file_line:
    if not line.startswith("#"):
        line_dict=line.split("|")
        server_ip_var=line_dict[0]
        server_address="10.42.11.7"+str(server_ip_var.split(".")[2][1:])
        user_name='admin'
        passwd_var=line_dict[1].strip('\n')
        if not server_address in server_run_list:
            server_run_list.append(server_address)
            get_url = 'PrismGateway/services/rest/v1/users/change_password'
            json_data = '{"oldPassword":"NuUniv/4u#","newPassword":"'+passwd_var+'"}'
            method = 'PUT'
            user = 'admin'
            passwd = 'NuUniv/4u#'
            value = ""
            response=get_json_data(server_address, get_url, json_data, method, user_name, passwd, value)
            if "true" in str(response).lower:
                print("Password changed to "+passwd_var+" on PC "+server_address)
            else:
                print("Password not changed to " + passwd_var + " on PC " + server_address+"! Please check using the GUI!")