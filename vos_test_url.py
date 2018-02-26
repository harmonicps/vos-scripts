#!/usr/bin/env python

###########################################################
# Script: vos_test_url.py
# Author: John Vasconcelos
# Date: 01/22/2018
# Version 1.1
###########################################################

import requests
import json
import vos
from kazoo.client import KazooClient
import sys
import datetime
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def build_url(serv,url_type,mdsip):
    ret_url = []
    if 'HLS' in url_type:
        ret_url.append("http://%s:20202/Content/%s/Live/channel(%s)/index_mobile.m3u8" %(mdsip,url_type,serv))
        ret_url.append("http://%s:20202/Content/%s/Live/channel(%s)/index_tv.m3u8" %(mdsip,url_type,serv))
    elif 'DASH' in url_type:
        ret_url.append("http://%s:20202/Content/%s/Live/channel(%s)/manifest_mobile.mpd" %(mdsip,url_type,serv))
        ret_url.append("http://%s:20202/Content/%s/Live/channel(%s)/manifest_tv.mpd" %(mdsip,url_type,serv))
    elif 'SS' in url_type:
        ret_url.append("http://%s:20202/Content/%s/Live/channel(%s).isml/Manifest_mobile" %(mdsip,url_type,serv))
        ret_url.append("http://%s:20202/Content/%s/Live/channel(%s).isml/Manifest_tv" %(mdsip,url_type,serv))    

    return ret_url

#Logfile Name Construction
now = datetime.datetime.now()
log_file = 'vos-url-check-' + now.strftime("%Y-%m-%d-%H%M") + '.log'

ntries = 2

vos_session = vos.vos_get_session()

url_types = ['HLS_hls.pr','HLS_hls.fp','HLS_hls.00','DASH_dash.wv','DASH_dash.00','SS_ss.pr','SS_ss.00']

#Find out the Mesos Master IP

zk = KazooClient(hosts='127.0.0.1:2181')
zk.start()

mesos_nodes_unsort = zk.get_children('/mesos/')
mesos_nodes = sorted(mesos_nodes_unsort)

mesos_master = zk.get('/mesos/'+mesos_nodes[0])

mesos_master_ip = json.loads(mesos_master[0])['address']['ip']


#Get list of Egress Nodes
mtasks = vos.mesos_get_tasks(mesos_master_ip)

magents = vos.mesos_get_agents(mesos_master_ip)

mds_nodes = vos.get_egress_mds_tasks(mtasks,magents)

vos_services = vos.vos_get_service_all('127.0.0.1',vos_session)

nurls = 0

for serv in vos_services.json():

    # Test URLs 

    for url_type in url_types:
        
        for mds in mds_nodes:

            urls = build_url(serv['name'],url_type,mds['nodeip'])
            
            for test_url in urls:
                print "Testing URL: %s" %test_url
                
                url_error = False
                for n in range(ntries):
                    req = vos_session.get(test_url)
                    if not req.status_code == 200:
                        vos.log_write('ERROR',"CODE: %s - URL %s" %(str(req.status_code),test_url),log_file)
                        url_error = True
                
                if not url_error:
                    vos.log_write('INFO',"URL GOOD: %s - URL %s" %(str(req.status_code),test_url),log_file)
                
                nurls+=1

vos.log_write('INFO',"%s URLs TESTED" %(str(nurls)),log_file)

                



