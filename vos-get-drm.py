#!/usr/bin/env python
######################################
# Script: vos-get-drm.py
# Author: Satish Botla
# Date: 08/15/2017
# Version 1.1
######################################
# vos.py needs to be in the same path as this script.
import json
import requests
import vos

vos_session = vos.vos_get_session("dfw.ote@gmail.com","dfwote*1")
api_proto = "https"
hostname = "10.105.163.3"
api_get_drm = "/vos-api/scrambling/v1/drm/systems"
api_get_services = "/vos-api/configure/v1/services"
api_header_json = {'user-agent':'Accept:application/json'}
api_header_all = {'user-agent':'Accept: */*'}
api_header_serv_post = {'Content-Type':'application/json' , 'Accept':'*/*'}
#vos_session = requests.Session()
#vos_session.auth = ('dfw.ote@gmail.com','dfwote*1')
vos_drm_req = vos_session.get(api_proto+'://'+hostname+api_get_drm,headers=api_header_json,verify=False)
vos_service_req = vos_session.get(api_proto+'://'+hostname+api_get_services,headers=api_header_json,verify=False)
data = vos_drm_req.json()
services = vos_service_req.json() 


print "EncrptionInterfaceID,EncrptionInterfacename,EncrptionInterfaceType,URL,id,name,packagingType,resourceId"
for enctypeid in data:
	list = []
	list.append(enctypeid['id'])
	list.append(enctypeid['name'])
	list.append(enctypeid['keyManagementServers'][0]['url'])
	list.append(enctypeid['encryptionInterfaceType'])
	for resource in enctypeid['resources']:
		for service in services:
			if(resource['id'] == service['addons']['drmAddon']['settings'][0]['resourceId']):
				print(list[0] + ',' + list[1] + ',' +list[2]+ ',' +list[3]+ ',' +resource['id']+ ',' +resource['name']+','+resource['packagingType']+','+resource['resourceId']+','+service['name']+','+str(service['addons']['drmAddon']['enable']))
			if(resource['id'] == service['addons']['drmAddon']['settings'][1]['resourceId']):
				print(list[0] + ',' + list[1] + ',' +list[2]+ ',' +list[3]+ ',' +resource['id']+ ',' +resource['name']+','+resource['packagingType']+','+resource['resourceId']+','+service['name']+','+str(service['addons']['drmAddon']['enable']))
			if(resource['id'] == service['addons']['drmAddon']['settings'][2]['resourceId']):
				print(list[0] + ',' + list[1] + ',' +list[2]+ ',' +list[3]+ ',' +resource['id']+ ',' +resource['name']+','+resource['packagingType']+','+resource['resourceId']+','+service['name']+','+str(service['addons']['drmAddon']['enable']))
			if(resource['id'] == service['addons']['drmAddon']['settings'][3]['resourceId']):
				print(list[0] + ',' + list[1] + ',' +list[2]+ ',' +list[3]+ ',' +resource['id']+ ',' +resource['name']+','+resource['packagingType']+','+resource['resourceId']+','+service['name']+','+str(service['addons']['drmAddon']['enable']))
	
#print "EncrptionInterfaceID,EncrptionInterfacename,EncrptionInterfaceType,URL,requestorId,id,name,packagingType,resourceId"
