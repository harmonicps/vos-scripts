#!/usr/bin/env python


###########################################################
# Script: vos_get_cl_info.py
# NOTE: THIS SCRIPT IS NOT SUPPORTED OR TESTED BY HARMONIC. 
#       USE IT AT YOUR OWN RISK !!!!
# Author: John Vasconcelos
# Date: 05/14/2017
# Version 1.1
###########################################################

# vos.py needs to be in the same path as this script.
import vos

vos_session = vos.vos_get_session("dfw.ote@gmail.com","dfwote*1")

vosrt = "vosdashboard.dfwcpcgreen.ds.dtvops.net"

cl_list = vos.vos_get_cl_list(vosrt,vos_session)


#cl_list.append({'clid':clid , 'clname':clname , 'clip':clip , 'clstate':clstate , 'clrate':clrate})
for cl in cl_list:

    print "%s,%s,%s,%s" %(cl['clname'] , cl['clip'] , cl['clstate'] , cl['clrate'])