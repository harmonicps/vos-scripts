#!/usr/bin/env python

###########################################################
# Script: vos_get_spare_infest_nodes.py
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

spare_ingest = []

#Create a CSV file containing the serf members output from the VOS cluster in question, and save it in the same path as the script.
f = open("serf-members.txt")

for line in f:
    is_spare = True
    l = line.split(",")
    node_name = l[0]
    for item in ingest_serv:
        if item['node'] == node_name:
            is_spare = False
    if is_spare and l[3].strip() == "role=live_ingest":
        node_ip = l[1].split(":")[0]
        spare_ingest.append({'node':node_name , 'nodeip':node_ip})

print "Spare Ingest Node,Node IP"

for spare in spare_ingest:
    print "%s,%s" %(spare['node'] , spare['nodeip'])
