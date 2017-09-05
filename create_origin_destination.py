#!/usr/bin/env python
######################################
# Script: create_origin_destination.py
# Date: 07/17/2017
# Version 1.1
# Author: Satish Botla
# Input: origin_create_parameters.csv
#         type,destination_name,redundancuMode,outputType,publishName,destinationProfileId respectively
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
file = open('origin_create_parameters.csv','r')
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
        "ipSettings": null,
        "originSettings": {
          "originOutputEndPoints": [
            {
              "id": str(uuid.uuid4()),
              "profileName": "dash.wv",
              "packagingProfileType": "e_DASH",
              "originOutputProtocol": "HTTPS",
              "hostname": "127.0.0.1",
              "port": 80,
              "path": "DASH",
              "username": "",
              "password": "******",
              "outputMonitor": False,
              "hostnameForMonitoring": "",
              "compatibilityMode": "STANDARD",
              "playbackUrl": null,
              "drm": null,
              "publishName": null
            },
            {
              "id": str(uuid.uuid4()),
              "profileName": "dash.00",
              "packagingProfileType": "e_DASH",
              "originOutputProtocol": "HTTPS",
              "hostname": "127.0.0.1",
              "port": 80,
              "path": "DASH",
              "username": "",
              "password": "******",
              "outputMonitor": False,
              "hostnameForMonitoring": "",
              "compatibilityMode": "STANDARD",
              "playbackUrl": null,
              "drm": null,
              "publishName": null
            },
            {
              "id": str(uuid.uuid4()),
              "profileName": "hls.pr",
              "packagingProfileType": "e_HLS",
              "originOutputProtocol": "HTTPS",
              "hostname": "127.0.0.1",
              "port": 80,
              "path": "HLS",
              "username": "",
              "password": "******",
              "outputMonitor": False,
              "hostnameForMonitoring": "",
              "compatibilityMode": "STANDARD",
              "playbackUrl": null,
              "drm": null,
              "publishName": null
            },
            {
              "id": str(uuid.uuid4()),
              "profileName": "hls.fp",
              "packagingProfileType": "e_HLS",
              "originOutputProtocol": "HTTPS",
              "hostname": "127.0.0.1",
              "port": 80,
              "path": "HLS",
              "username": "",
              "password": "******",
              "outputMonitor": False,
              "hostnameForMonitoring": "",
              "compatibilityMode": "STANDARD",
              "playbackUrl": null,
              "drm": null,
              "publishName": null
            },
            {
              "id": str(uuid.uuid4()),
              "profileName": "hls.00",
              "packagingProfileType": "e_HLS",
              "originOutputProtocol": "HTTPS",
              "hostname": "127.0.0.1",
              "port": 80,
              "path": "HLS",
              "username": "",
              "password": "******",
              "outputMonitor": False,
              "hostnameForMonitoring": "",
              "compatibilityMode": "STANDARD",
              "playbackUrl": null,
              "drm": null,
              "publishName": null
            },
            {
              "id": str(uuid.uuid4()),
              "profileName": null,
              "packagingProfileType": "e_INTERNAL",
              "originOutputProtocol": "HTTPS",
              "hostname": "127.0.0.1",
              "port": 80,
              "path": "INTERNAL",
              "username": "",
              "password": "******",
              "outputMonitor": False,
              "hostnameForMonitoring": "",
              "compatibilityMode": "STANDARD",
              "playbackUrl": null,
              "drm": null,
              "publishName": line[4]
            },
            {
              "id": str(uuid.uuid4()),
              "profileName": "ss.pr",
              "packagingProfileType": "e_SS",
              "originOutputProtocol": "HTTPS",
              "hostname": "127.0.0.1",
              "port": 80,
              "path": "SS",
              "username": "",
              "password": "******",
              "outputMonitor": False,
              "hostnameForMonitoring": "",
              "compatibilityMode": "STANDARD",
              "playbackUrl": null,
              "drm": null,
              "publishName": null
            },
            {
              "id": str(uuid.uuid4()),
              "profileName": "ss.00",
              "packagingProfileType": "e_SS",
              "originOutputProtocol": "HTTPS",
              "hostname": "127.0.0.1",
              "port": 80,
              "path": "SS",
              "username": "",
              "password": "******",
              "outputMonitor": False,
              "hostnameForMonitoring": "",
              "compatibilityMode": "STANDARD",
              "playbackUrl": null,
              "drm": null,
              "publishName": null
            }
          ]
        }
      }
    ],
    "destinationProfileId": line[5],
    "embeddedDestinationProfile": null
  }
        info_as_json = json.dumps(data)
        print(info_as_json)
        api_proto = "https"
        hostname = raw_input("Enter the VOS RT Address:\n")
        vos_session = vos.vos_get_session()
        api_post_dest = "/vos-api/configure/v1/destinations"
	api_get_destinations = "/vos-api/configure/v1/destinations"
        api_header_json = {'user-agent':'Accept:application/json'}
        api_header_serv_post = {'Content-Type':'application/json' , 'Accept':'*/*'}
	vos_ats_get_req = vos_session.get(api_proto+'://'+hostname+api_get_destinations+'?'+'name='+data['name'],headers=api_header_json,verify=False)
	responsebody = vos_ats_get_req.json()
	if(responsebody != []):
	    print('destination already created')
	else:	
            vos_ats_req = vos_session.post(api_proto+'://'+hostname+api_post_dest,headers=api_header_serv_post,data=info_as_json,verify=False)
	    print(vos_ats_req.json())
            if vos_ats_req.status_code != 200:
                print("Error Posting the destination")
                sys.exit(2)
            else:
                count = count+1
                print('Destination added successfully :' +line[0] + ',' + line[1]+ ',' + line[3]+ ',' + line[4]+ ',' + line[5])
                time.sleep(20)
print(count , " destinations added")
