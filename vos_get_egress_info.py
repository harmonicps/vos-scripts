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

vos_session = vos.vos_get_session("dfw.ote@gmail.com","dfwote*1")

mesos_master = "10.105.168.19"

vosrt = "vosdashboard.dfwcpcgreen.ds.dtvops.net"

mtasks = vos.mesos_get_tasks(mesos_master)

magents = vos.mesos_get_agents(mesos_master)


lio_nodes = get_egress_lio_tasks(mtasks,magents,vosrt,vos_session)

mds_nodes = get_egress_mds_tasks(mtasks,magents)


#{'node':ahostname , 'nodeip':agentip , 'groupid':groupid, 'noderole':noderole ,'liopoints': groupid , 'state':originstate}


f_lio = open("node_lio_info.txt","w")
for lio in lio_nodes:

    f_lio.write("%s, %s, %s" %(lio['node'] , lio['nodeip'] , lio['groupid'], lio['noderole']))

f_lio.close()

f_mds = open("node_mds_info.txt","w")
for mds in mds_nodes:

    f_mds.write("%s, %s, %s" %(mds['node'] , mds['nodeip'] , mds['Type']))

f_mds.close()