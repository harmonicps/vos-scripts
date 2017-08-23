#!/usr/bin/env python

###########################################################
# Script: vos_get_source.py
# Author: John Vasconcelos
# Date: 04/24/2017
# Version 1.0
###########################################################

from pprint import pprint
import requests
import json


requests.packages.urllib3.disable_warnings()

api_proto = "https"

hostname = "vosdashboard.dfwcpcgreen.ds.dtvops.net"

api_get_src = "/vos-api/configure/v1/sources"

api_get_cl = "/vos-api/uplink-hub/v1/uplinkGroups"

api_header_json = {'user-agent':'Accept:application/json'}

api_header_all = {'user-agent':'Accept: */*'}


sr_sh_name = ["AandE.AandEHD-1382.1080.eng.p","AMC.AMCHD-4730.1080.eng.p","Bravo.BRVOHD-1323.1080.eng.p","CNBC.CNBCHD-1328.1080.eng.p","E.EHD-1593.1080.eng.p","FYI.FYIHD-1422.1080.eng.p","GolfChannel.GolfHD-1324.1080.eng.p","HISTORY.HISTHD-1557.1080.eng.p","IFC.IFCHD-4733.1080.eng.p","Lifetime.LIFEHD-1903.1080.eng.p","LifetimeMovieNetwork.LMNHD-1949.1080.eng.p","MSNBC.mnbcHD-1590.1080.eng.p","NBCSportsNetwork.NBCSHD-1325.1080.eng.p","NBCUniverso.UVSOHD-1320.1080.esp","Oxygen.OXGNHD-1782.1080.eng.p","Sprout.SPRTHD-295.1080.eng.p","Sundance.SUNDHD-4734.1080.eng.p","Syfy.SyfyHD-1326.1080.eng.p","USANetwork.USAHD-1327.1080.eng.p","Viceland.H2HD-1936.1080.eng.p","Wetv.WEHD-4731.1080.eng.p"]


vos_session = requests.Session()
vos_session.auth = ('dfw.ote@gmail.com','dfwote*1')

vos_session.post(api_proto+'://'+hostname, verify=False)

vos_cl_req = vos_session.get(api_proto+'://'+hostname+api_get_cl,headers=api_header_json,verify=False)

cl = vos_cl_req.json()

for i in sr_sh_name:
    api_get_src = "/vos-api/configure/v1/sources?name=" + i

    vos_sour_req = vos_session.get(api_proto+'://'+hostname+api_get_src,headers=api_header_all,verify=False)

    sr = vos_sour_req.json()

    for sritem in sr:
        sr_id = sritem['id']
        sr_name =  sritem['name']
        sr_clid = sritem['inputs'][0]['zixiSettings']['harmonicUplinkSetting']['uplinkGroupId']
        sr_sip = sritem['inputs'][0]['zixiSettings']['harmonicUplinkSetting']['ssmIpAddresses'][0]
        sr_mip = sritem['inputs'][0]['zixiSettings']['harmonicUplinkSetting']['ipAddress']
        sr_udp = str(sritem['inputs'][0]['zixiSettings']['harmonicUplinkSetting']['ipPort'])
        for citem in cl:
            c_id = citem['id']
            if c_id == sr_clid:
                sr_cl = citem['name']
                break
            else:
                sr_cl = "NA"

    print '*'.join((sr_name,sr_id,sr_cl,sr_clid,sr_sip,sr_mip,sr_udp))