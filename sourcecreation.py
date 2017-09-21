#!/usr/bin/env python
######################################
# Script: sourcecreation.py
# Author: Satish Botla
# Input: sourceinfo.csv
# csv file which has name,cloudlink,ipAddress,ipPort,ssmIpAddresses,slateimageId respectively
# Date: 08/15/2017
# Version 1.1
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
file = open('sourceinfo.csv','r')
reader = csv.reader(file)
count = 0
for line in reader:
    api_proto = "https"
    hostname = raw_input("Enter the VOS RT Address:\n")
    vos_session = vos.vos_get_session()
    api_get_cloudlink = "/vos-api/uplink-hub/v1/uplinkGroups"
    api_header_json = {'user-agent':'Accept:application/json'}
    vos_cloudlink_get_req = vos_session.get(api_proto+'://'+hostname+api_get_cloudlink,headers=api_header_json,verify=False)
    cloudlinkresponsebody = vos_cloudlink_get_req.json()
    for cloudlink in cloudlinkresponsebody:
        if(cloudlink['name'] == line[1]):
	    uplinkGroupId = cloudlink['id']
            print(uplinkGroupId)
    data = {
    "id": "",
    "labels": [],
    "name": line[0],
    "inputs": [
      {
        "id": str(uuid.uuid4()),
        "rank": 1,
        "type": "ZIXI",
        "ipSettings": null,
        "slateSettings": null,
        "zixiSettings": {
          "programNum": 0,
          "programName": "",
          "grooming": null,
          "zixiInputType": "HARMONIC_UPLINK",
          "harmonicUplinkSetting": {
            "uplinkId": null,
            "uplinkGroupId": uplinkGroupId,
            "ipAddress": line[2],
            "ipPort": line[3],
            "ipPortRangeEnd": 0,
            "ssmIpAddresses": [
              line[4]
            ],
            "zixiEndPointSetting": {
              "zixiEndpointId": null,
              "recvAddress": null,
              "recvPort": 0
            },
            "zixiEndPointSettingList": null
          },
          "encoderSetting": null,
          "zixiEndPointSetting": {
            "zixiEndpointId": null,
            "recvAddress": null,
            "recvPort": 0
          }
        },
        "hspSettings": null
      },
      {
        "id": str(uuid.uuid4()),
        "rank": 2,
        "type": "SLATE",
        "ipSettings": null,
        "slateSettings": {
          "type": "SIGNAL_LOSS",
          "imageId": line[5],
          "customSlateSettings": null
        },
        "zixiSettings": null,
        "hspSettings": null
      }
    ],
    "pmtPid": null,
    "enableMonitoring": false
  }

    info_as_json = json.dumps(data)
    print(info_as_json)
    api_get_source = "/vos-api/configure/v1/sources"
    api_post_source = "/vos-api/configure/v1/sources"
    api_header_serv_post = {'Content-Type':'application/json' , 'Accept':'*/*'}
    # Get request to sources api for checking the for source duplication
    vos_src_get_req = vos_session.get(api_proto+'://'+hostname+api_get_source+'?'+'name='+data['name'],headers=api_header_json,verify=False)
    responsebody = vos_src_get_req.json()
    if(responsebody != []):
        print('Source already created')
    else:	
        # Post request to create a new source
        vos_src_req = vos_session.post(api_proto+'://'+hostname+api_post_source,headers=api_header_serv_post,data=info_as_json,verify=False)
        if vos_src_req.status_code != 200:
            print("Error Posting the source")
            sys.exit(2)
        else:
            count = count+1
            print('Source added successfully :' +line[0] + ',' + line[1]+ ',' + line[2]+ ',' + line[3]+ ',' + line[4])
            time.sleep(10)
print(count , " sources added")


