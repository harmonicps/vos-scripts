#!/usr/bin/env python


###########################################################
# Script: vos_get_lio_serv.py
# NOTE: THIS SCRIPT IS NOT SUPPORTED OR TESTED BY HARMONIC.
#       USE IT AT YOUR OWN RISK !!!!
# Author: John Vasconcelos
# Date: 06/05/2017
# Version 1.1
###########################################################

# vos.py needs to be in the same path as this script.
import vos

vos_session = vos.vos_get_session("dfw.ote@gmail.com","dfwote*1")

mesos_master = "10.105.168.19"

vosrt = "vosdashboard.dfwcpcgreen.ds.dtvops.net"

mtasks = vos.mesos_get_tasks(mesos_master)

magents = vos.mesos_get_agents(mesos_master)

lio_info = vos.vos_get_live_ingest(mtasks,magents,vosrt,vos_session)


print "SERVICE,LIO ID,PACKAGE,NODE,NODE IP,STATE"

for lio in lio_info:
    print "%s,%s,%s,%s,%s,%s" %(lio['servname'] , lio['lioid'] , lio['package'] , lio['node'] , lio['nodeip'] , lio['state'])
