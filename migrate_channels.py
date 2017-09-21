#!/usr/bin/env python

###########################################################
# Script: migrate_channels.py
# NOTE: THIS SCRIPT IS NOT SUPPORTED OR TESTED BY HARMONIC.
#       USE IT AT YOUR OWN RISK !!!!
# Script to migrate sources, destinations and services from sources.json,
# destinations.json and services.json to a new cluster.
# Inputs: 
#         sources.json - get request from all the sources in the old system
#         destinations.json - get request for all the destinations in the old system.
#         services.json - get requeest for all the services in the old system.
#         channellist.csv - CSV file which contains the source name, origin destination name, ats destination name, mobile service name and tv service name in respective order. 
# Author: Satish Botla
# Date: 08/03/2017
# Version 1.1
###########################################################

import csv
import vos
import yaml, json
import uuid
import time
import requests

vosrt = raw_input("Enter the VOS RT Address:\n")
vos_session = vos.vos_get_session()
# input json which holds all the sources information in json format.
sources = json.load(open('sources.json'))
# input json which holds all the destinations information in json format.
destinations = json.load(open('destinations.json'))
# input json which holds all the services information in json format.
services = json.load(open('services.json'))



file = open('channellist.csv','r')
reader = csv.reader(file)
for line in reader:
    for sour in sources:
        if(sour['name'] == line[0]):
            info_as_json = json.dumps(sour)
            print info_as_json
            print vos_add_source(info_as_json,vosrt,vos_session)
            time.sleep(10)
    for dest in destinations:
        if line[1]:
            if(dest['name'] == line[1]):
                ori_destination_as_json = json.dumps(dest)
                print ori_destination_as_json
                print vos_destination_add(ori_destination_as_json,vosrt,vos_session)
                time.sleep(10)
        if  line[2]:
            if(dest['name'] == line[2]):
                ats_destination_as_json = json.dumps(dest)
                print ats_destination_as_json
                print vos_destination_add(ats_destination_as_json,vosrt,vos_session)
                time.sleep(10)
    for serv in services:
        if line[3]:
            if(serv['name'] == line[3]):
                mobileservice_as_json = json.dumps(serv)
                print service_as_json
                print vos_service_add(mobileservice_as_json,vosrt,vos_session)
                time.sleep(10)
        if line[4]:
            if(serv['name'] == line[4]):
                tvservice_as_json = json.dumps(serv)
                print tvservice_as_json
                print vos_service_add(tvservice_as_json,vosrt,vos_session)
                time.sleep(10)

""" Function to create a vos session """
def vos_get_session(user="",passwd=""):
    
    if not user or not passwd:
        user = raw_input("Enter the Username for VOS:\n")
        passwd = getpass.getpass("Enter the Password:\n")

    vos_session = requests.Session()
    vos_session.auth = (user,passwd)

    return vos_session    

""" Function to add a new source in the vos."""
def vos_add_source(param,vosrt,session="",proto="https"):
    if not session:
        session = vos_get_session()
    api_header = {'Content-Type':'application/json' , 'Accept':'*/*'}
    uri = proto+'://'+vosrt+"/vos-api/configure/v1/sources"
    ret = session.post(uri,headers=api_header,data=param,verify=False)
    new_source = ret.json()
    if ret.status_code == 200:
        print "Service %s with ID %s created with the following Params:\n" %(new_source['name'] , new_source['id'])
        print param
        print "\n"
    else:
        print "Error creating service with Error: %s" %ret
    return ret

"""" Function to add a new destination in the vos."""
def vos_destination_add(param,vosrt,session="",proto="https"):
    if not session:
        session = vos_get_session()
    api_header = {'Content-Type':'application/json' , 'Accept':'*/*'}
    uri = proto+'://'+vosrt+"/vos-api/configure/v1/destinations"
    ret = session.post(uri,headers=api_header,data=param,verify=False)
    new_dst = ret.json()
    if ret.status_code == 200:
        print "Service %s with ID %s created with the following Params:\n" %(new_dst['name'] , new_dst['id'])
        print param
        print "\n"
    else:
        print "Error creating destination with Error: %s" %ret
    return ret

"""" Function to add a new service in the vos."""
def vos_service_add(param,vosrt,session="",proto="https"):
    if not session:
        session = vos_get_session()
    api_header = {'Content-Type':'application/json' , 'Accept':'*/*'}
    uri = proto+'://'+vosrt+"/vos-api/configure/v1/services"
    ret = session.post(uri,headers=api_header,data=param,verify=False)
    new_srv = ret.json()
    if ret.status_code == 200:
        print "Service %s with ID %s created with the following Params:\n" %(new_srv['name'] , new_srv['id'])
        print param
        print "\n"
    else:
        print "Error creating service with Error: %s" %ret
    return ret

if __name__ == "__main__":
    main(sys.argv[1:])
