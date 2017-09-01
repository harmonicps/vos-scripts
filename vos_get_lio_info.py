#!/usr/bin/env python


###########################################################
# Script: vos_get_lio_info.py
# NOTE: THIS SCRIPT IS NOT SUPPORTED OR TESTED BY HARMONIC. 
#       USE IT AT YOUR OWN RISK !!!!
# Author: John Vasconcelos
# Date: 05/14/2017
# Version 1.1
###########################################################

# vos.py needs to be in the same path as this script.
import vos

vosrt = raw_input("Enter the VOS RT Address:\n")

vos_session = vos.vos_get_session()

mesos_master = raw_input("Enter the IP of the Mesos Master:\n")

mtasks = vos.mesos_get_tasks(mesos_master)

magents = vos.mesos_get_agents(mesos_master)

lio_info = vos.vos_get_live_ingest(mtasks,magents,vosrt,vos_session)


print "SERVICE,PACKAGE,NODE,NODEIP,STATE"

for lio in lio_info:
    print "%s,%s,%s,%s,%s" %(lio['servname'] , lio['package'] , lio['node'] , lio['nodeip'] , lio['state'])
