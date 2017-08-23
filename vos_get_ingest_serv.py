#!/usr/bin/env python

###########################################################
# Script: vos_get_ingest_serv.py
# NOTE: THIS SCRIPT IS NOT SUPPORTED OR TESTED BY HARMONIC. 
#       USE IT AT YOUR OWN RISK !!!!
# Author: John Vasconcelos
# Date: 05/14/2017
# Version 1.1
###########################################################

# vos.py needs to be in the same path as this script.
import vos

mesos_master = "10.105.168.19"

magents = vos.mesos_get_agents(mesos_master)

mtasks = vos.mesos_get_tasks(mesos_master)

ingest_serv = vos.get_ingest_services(mtasks,magents)

print "SERVICE,INGEST NODE,NODE IPs"

for serv in ingest_serv:
    print "%s,%s,%s" %(serv['service'] , serv['node'] , serv['nodeip'])
