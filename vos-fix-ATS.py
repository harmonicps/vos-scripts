#!/usr/bin/env python

###########################################################
# Script: vos_fix_ATS.py
# Author: John Vasconcelos
# Date: 04/20/2017
# Version 1.1
###########################################################

import requests
import json,yaml
import time
import vos

requests.packages.urllib3.disable_warnings()

api_proto = "https"

hostname = raw_input("Enter the VOS RT Address:\n")

vos_session = vos.vos_get_session()

api_get_serv = "/vos-api/configure/v1/services"

api_get_dest = "/vos-api/configure/v1/destinations"

api_header_json = {'user-agent':'Accept:application/json'}

api_header_all = {'user-agent':'Accept: */*'}

api_header_serv_post = {'Content-Type':'application/json' , 'Accept':'*/*'}

api_header_serv_post = {'Content-Type':'application/json' , 'Accept':'*/*'}

vos_session.post(api_proto+'://'+hostname, verify=False)



def del_serv(srvid):
    api_del_serv = "/vos-api/configure/v1/services/" + srvid
    del_srv = vos_session.delete(api_proto+'://'+hostname+api_del_serv,headers=api_header_all,verify=False)
    return del_srv.text

def get_serv(srvname):

     api_srv_get = "/vos-api/configure/v1/services?serviceName=" + srvname
     print srvname
     srv_get = vos_session.get(api_proto+'://'+hostname+api_srv_get,headers=api_header_all,verify=False)
     servs = yaml.safe_load(srv_get.text)

     for i in servs:
        if not 'ATS' in i['name']:
            ret = i


     return ret




vos_serv_req = vos_session.get(api_proto+'://'+hostname+api_get_serv,headers=api_header_all,verify=False)

vos_dest_req = vos_session.get(api_proto+'://'+hostname+api_get_dest,headers=api_header_json,verify=False)

sv = vos_serv_req.json()

d = vos_dest_req.json()


for svitem in sv:
    sv_id =  svitem['id']
    sv_name =  svitem['name']
    sv_dest_id = svitem['destinationId']

    for ditem in d:
        d_id = ditem['id']
        d_type = ditem['type']
        d_name = ditem['name']
        
        if d_id == sv_dest_id and "ATS" in sv_name:

            #Deletes the ATS Service
            print "Deleting SERVICE: %s SERVICE ID: %s ... \n\n" %(sv_name,sv_id) 
            print del_serv(sv_id)
            time.sleep(600)

            sv_orig = sv_name.split(".")

            sv_orig.pop()

            sv_orig = ".".join(sv_orig)

            print "Searching for SERVICE: " + sv_orig + "...... \n\n"

            sv_mod = get_serv(sv_orig)

            sv_mod['destinationsId'].append(sv_dest_id)

            sv_mod_j = json.dumps(sv_mod)

            print "Modifying service %s with the following settings  \n\n" %(sv_mod_j['id'])

            print sv_mod_j + "\n\n\n"

            param = sv_mod_j

            api_put_serv = "/vos-api/configure/v1/services/" + sv_mod_j['id']

            vos_serv_put = vos_session.put(api_proto+'://'+hostname+api_put_serv,headers=api_header_put,data=param,verify=False)

            print vos_serv_put.text

            time.sleep(600)
