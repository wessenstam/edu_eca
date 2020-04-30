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
def get_json_data(ip_address,get_url,json_data,method,user,passwd,value):
    #Get the URL and compose the command to get the request from the REST API of the cluster
    url="https://"+ip_address+":9440/"+get_url
    header_post = {'Content-type': 'application/json'}
    # if method is not set assume GET
    if method=="":
        method="get"

    # Set the right requests based on GET or POST
    if method.lower()=="get":
        try:
            page=requests.get(url,verify=False,auth=(user,passwd),timeout=15)
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

    elif method.lower()=="post":
        try:
            page=requests.post(url, verify=False, auth=(user, passwd), data=json_data, headers=header_post,timeout=15)
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
            page=requests.put(url, verify=False, auth=(user, passwd), data=json_data, headers=header_post,timeout=15)
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
# Deploy Clusters
#####################################################################################################################################################################

def deploy_cluster(server_ip,user,passwd):

    print("------------------------------------------------")
    print("- PE at " + server_ip)

    # 1. Accept the EULA
    url = "PrismGateway/services/rest/v1/eulas/accept"
    payload = '{"username":"TechEnablement EMEA","companyName":"Nutanix","jobTitle":"Nutanix"}'
    value = ""
    method = "POST"
    json_search = get_json_data(server_ip, url, payload, method, user, passwd, value)

    # 2. Disable Pulse
    url = "PrismGateway/services/rest/v1/pulse"
    payload = '{"enable":"false","enableDefaultNutanixEmail":"false","isPulsePromptNeeded":"false"}'
    value = ""
    method = "PUT"
    json_search = get_json_data(server_ip, url, payload, method, user, passwd, value)


    # 3. Upload the images
    source_ip = "10.42.11.100"

    images = ("CentOS-7-x86_64-DVD-1908.iso","CentOS.qcow2","CubicDesignTools.iso","ECA_5.15.tar","move-3.4.1.qcow2","Nutanix-VirtIO-1.1.5.iso","Windows 2012 R2 Server.iso","Windows2012R2.qcow2")
    for image_check in sorted(images):
        if "qcow2" in str(image_check):
            image_type="DISK_IMAGE"
        else:
            image_type="ISO_IMAGE"

        _http_body ='{"action_on_failure":"CONTINUE","execution_order":"SEQUENTIAL","api_request_list":[{"operation":"POST","path_and_params":"/api/nutanix/v3/images","body":{"spec":{"name":"'+image_check+'", "description":"'+image_check+'", "resources":{"image_type":"'+image_type+'","source_uri":"http://'+source_ip+"/"+image_check+'"}},"metadata":{"kind":"image"}, "api_version":"3.1.0"}}], "api_version":"3.0"}'
        header_post = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        url="https://"+server_ip+':9440/api/nutanix/v3/batch'
        start_counter_measures(url,_http_body,user,passwd,header_post)

#####################################################################################################################################################################
# Start the countermeasures for the API calls to correct issues found
#####################################################################################################################################################################

def start_counter_measures(url, pay_load, user, passwd,header_post):
    try:
        page = requests.post(url, verify=False, auth=(user, passwd), data=pay_load, headers=header_post)
        page.raise_for_status()
        return page.json()
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

# Use a file with parameters to run the checks
file=open("cluster.txt","r")
file_line=file.readlines()
for line in file_line:
    if "#" not in line:
        line_dict=line.split("|")
        server_ip_var=line_dict[0]
        user_name='admin'
        passwd_var=line_dict[1]
        checks_to_run(server_ip_var,user_name,passwd_var)
