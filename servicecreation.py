#!/usr/bin/env python
######################################
# Script: servicecreation.py
# Author: Satish Botla
# Input: serviceinfo.csv
# csv file which has serviceName,primarySourcename,secondarySourcename,transcoding_profile_name,Origin_Destination_name,Ats_Destination_name,scte35Slate_imageId respectively.
# Date: 08/15/2017
# Version 1.1
######################################
import csv
import json
import vos
import requests
import sys
import time
import uuid


null = None
false = False
file = open('serviceinfo.csv','r')
reader = csv.reader(file)
count = 0
sourceId2 = ""
destinationIdsATS = ""
api_proto = "https"
hostname = "10.105.163.3"
api_get_source = "/vos-api/configure/v1/sources"
api_get_destination = "/vos-api/configure/v1/destinations"
api_get_transcodingProfileId = "/vos-api/labwizard/v1/profiles"
api_header_json = {'user-agent':'Accept:application/json'}
api_header_serv_post = {'Content-Type':'application/json' , 'Accept':'*/*'}
vos_session = requests.Session()
vos_session.auth = ('dfw.ote@gmail.com','dfwote*1')
vos_source_get_req = vos_session.get(api_proto+'://'+hostname+api_get_source,headers=api_header_json,verify=False)
vos_destination_get_req = vos_session.get(api_proto+'://'+hostname+api_get_destination,headers=api_header_json,verify=False)
vos_profileId_get_req = vos_session.get(api_proto+'://'+hostname+api_get_transcodingProfileId,headers=api_header_serv_post,verify=False)
sourcesresponsebody = vos_source_get_req.json()
destinationsresponsebody = vos_destination_get_req.json()
profileIdsresponsebody = vos_profileId_get_req.json()


for line in reader:
    for source in sourcesresponsebody:
        if(source['name'] == line[1]):
	    sourceId1 = source['id']
	    programNum = source['inputs'][0]['zixiSettings']['programNum']
            print('source1:'+ sourceId1,programNum)
	if(source['name'] == line[2]):
	    sourceId2 = source['id']
            print('Source2:'+sourceId2)
    for destination in destinationsresponsebody:
	if(destination['name'] == line[4]):
	    destinationIdorigin = destination['id']
            print("Origin:" +destinationIdorigin)
	if(destination['name'] == line[5]):
	    destinationIdsATS = destination['id']
            print('ATS:'+destinationIdsATS)
    for profile in profileIdsresponsebody:
	if(profile['name'] == line[3].rsplit(' ',1)[0]):
	    version = line[3][-1:]
	    if(profile['customerVersion'] == version):
	        profileId = profile['id']
                print('ProfileId:'+profileId, version)
	    else:
		continue
    # Condition to check if the Service has ATS Destination
    if(destinationIdsATS):
        # Condition to check if the Service has SecondaryService
        if(sourceId2):
	    data = {
    "id": "",
    "name": line[0],
    "programNum": programNum,
    "serviceSources": [
      {
        "sourceId": sourceId1,
        "rank": 1
      },
      {
        "sourceId": sourceId2,
        "rank": 2
      }
    ],
    "profileId": profileId,
    "embeddedProfiles": null,
    "destinationId": destinationIdorigin,
    "destinationsId": [
      destinationIdsATS,
      destinationIdorigin
    ],
    "timeShiftWindow": null,
    "addons": {
      "logoAddon": null,
      "graphicsAddon": null,
      "videoInsertionAddon": null,
      "trafficAddon": null,
      "casAddon": null,
      "drmAddon": null,
      "scte35SlateAddon": {
        "imageId": line[6]
      },
      "resourceSettingsAddon": null
    },
    "controlState": "OFF",
    "redundancyMode": "OFF",
    "rank": "",
    "processingEngineVersion": null,
    "processingEngine": null,
    "version": null
  }
        # Condition to check if the Service don't have SecondarySource
        else:
    	    data = {
    "id": "",
    "name": line[0],
    "programNum": programNum,
    "serviceSources": [
      {
        "sourceId": sourceId1,
        "rank": 1
      }
    ],
    "profileId": profileId,
    "embeddedProfiles": null,
    "destinationId": destinationIdorigin,
    "destinationsId": [
      destinationIdsATS,
      destinationIdorigin
    ],
    "timeShiftWindow": null,
    "addons": {
      "logoAddon": null,
      "graphicsAddon": null,
      "videoInsertionAddon": null,
      "trafficAddon": null,
      "casAddon": null,
      "drmAddon": null,
      "scte35SlateAddon": {
        "imageId": line[6]
      },
      "resourceSettingsAddon": null
    },
    "controlState": "OFF",
    "redundancyMode": "OFF",
    "rank": "",
    "processingEngineVersion": null,
    "processingEngine": null,
    "version": null
  }
    # Condition to check if the Service don't have ATS Destination
    else:
        # Condition to check if the Service has SecondarySource
        if(sourceId2):
	    data = {
    "id": "",
    "name": line[0],
    "programNum": programNum,
    "serviceSources": [
      {
        "sourceId": sourceId1,
        "rank": 1
      },
      {
        "sourceId": sourceId2,
        "rank": 2
      }
    ],
    "profileId": profileId,
    "embeddedProfiles": null,
    "destinationId": destinationIdorigin,
    "destinationsId": [
      destinationIdorigin
    ],
    "timeShiftWindow": null,
    "addons": {
      "logoAddon": null,
      "graphicsAddon": null,
      "videoInsertionAddon": null,
      "trafficAddon": null,
      "casAddon": null,
      "drmAddon": null,
      "scte35SlateAddon": {
        "imageId": line[6]
      },
      "resourceSettingsAddon": null
    },
    "controlState": "OFF",
    "redundancyMode": "OFF",
    "rank": "",
    "processingEngineVersion": null,
    "processingEngine": null,
    "version": null
  }
        # Condition to check if the Service don't have SecondaryService
        else:
    	    data = {
    "id": "",
    "name": line[0],
    "programNum": programNum,
    "serviceSources": [
      {
        "sourceId": sourceId1,
        "rank": 1
      }
    ],
    "profileId": profileId,
    "embeddedProfiles": null,
    "destinationId": destinationIdorigin,
    "destinationsId": [
      destinationIdorigin
    ],
    "timeShiftWindow": null,
    "addons": {
      "logoAddon": null,
      "graphicsAddon": null,
      "videoInsertionAddon": null,
      "trafficAddon": null,
      "casAddon": null,
      "drmAddon": null,
      "scte35SlateAddon": {
        "imageId": line[6]
      },
      "resourceSettingsAddon": null
    },
    "controlState": "OFF",
    "redundancyMode": "OFF",
    "rank": "",
    "processingEngineVersion": null,
    "processingEngine": null,
    "version": null
  }

    info_as_json = json.dumps(data)
    print(info_as_json)
    api_get_service = "/vos-api/configure/v1/services"
    api_post_service = "/vos-api/configure/v1/services"
    vos_service_get_req = vos_session.get(api_proto+'://'+hostname+api_get_service+'?'+'name='+data['name'],headers=api_header_json,verify=False)
    responsebody = vos_service_get_req.json()
    if(responsebody != []):
        print('Service already created')
    else:	
	# Post request to create a new service
        vos_service_req = vos_session.post(api_proto+'://'+hostname+api_post_service,headers=api_header_serv_post,data=info_as_json,verify=False)
        if vos_service_req.status_code != 200:
            print("Error Posting the service")
            sys.exit(2)
        else:
            count = count+1
            print('Service added successfully :' +line[0] + ',' + line[1]+ ',' + line[2]+ ',' + line[3]+ ',' + line[4]+ ',' + line[5])
            time.sleep(10)
print(count , " services added")
