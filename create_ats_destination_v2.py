#!/usr/bin/env python
######################################
# Script: create_ats_destination_v2.py
# Date: 07/17/2017
# Author: Satish Botla
# Version 2
# Input: ats_create_parameters.csv
        type,destinationname,redundancyMode,outputType,ipAddress,ipPort,cloudlinkGroupId,destinationProfileId respectively.
######################################
import csv
import json
# vos.py needs to be in the same path as this script.
import vos
import requests
import sys
import time
import uuid

null = None
false = False
file = open('ats_create_parameters_2017-07-17.csv','r')
reader = csv.reader(file)
count = 0

for line in reader:
        data = {
  "id": "",
  "type": line[0],
  "labels": [],
  "name": line[1],
  "outputs": [
    {
      "id": str(uuid.uuid4()),
      "redundancyMode": line[2],
      "rank": 1,
      "outputType": line[3],
      "ipSettings": {
        "ipNetworkAddress": null,
        "ipAddress": line[4],
        "ipPort": line[5],
        "cloudlinkGroupId": line[6],
        "cloudlinkId": null,
        "outputMonitor": False,
        "ipAddressForMonitoring": null,
        "ipPortForMonitoring": 0
      },
      "originSettings": null
    }
  ],
  "destinationProfileId": line[7],
  "embeddedDestinationProfile": null
}
        info_as_json = json.dumps(data)
        api_proto = "https"
        hostname = raw_input("Enter the VOS RT Address:\n")
        vos_session = vos.vos_get_session()
        api_post_dest = "/vos-api/configure/v1/destinations"
	api_get_destinations = "/vos-api/configure/v1/destinations"
        api_header_json = {'user-agent':'Accept:application/json'}
        api_header_serv_post = {'Content-Type':'application/json' , 'Accept':'*/*'}
	vos_ats_get_req = vos_session.get(api_proto+'://'+hostname+api_get_destinations+'?'+'name='+data['name'],headers=api_header_json,verify=False)
	responsebody = vos_ats_get_req.json()
        print(responsebody)
	if(responsebody != []):
	    print('destination already created')
	else:	
            vos_ats_req = vos_session.post(api_proto+'://'+hostname+api_post_dest,headers=api_header_serv_post,data=info_as_json,verify=False)
            if vos_ats_req.status_code != 200:
                print("Error Posting the destination")
                sys.exit(2)
            else:
                count = count+1
                print('Destination added successfully :' +line[0] + ',' + line[1]+ ',' + line[4]+ ',' + line[5]+ ',' + line[7])
                time.sleep(10)
print(count , " destinations added")

