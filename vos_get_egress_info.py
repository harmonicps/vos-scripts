#!/usr/bin/env python


###########################################################
# Script: vos_get_egress_info.py
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


lio_nodes = vos.get_egress_lio_tasks(mtasks,magents,vosrt,vos_session)

mds_nodes = vos.get_egress_mds_tasks(mtasks,magents)


#{'node':ahostname , 'nodeip':agentip , 'groupid':groupid, 'noderole':noderole ,'liopoints': groupid , 'state':originstate}


f_lio = open("node_lio_info.txt","w")
for lio in lio_nodes:

    f_lio.write("%s,%s,%s,%s\n" %(lio['node'] , lio['nodeip'] , lio['groupid'], lio['noderole']))

f_lio.close()

f_mds = open("node_mds_info.txt","w")
for mds in mds_nodes:

    f_mds.write("%s,%s,%s\n" %(mds['node'] , mds['nodeip'] , mds['Type']))

f_mds.close()