#!/usr/bin/env python


###########################################################
# Script: vos_migrate_services.py
# NOTE: THIS SCRIPT IS NOT SUPPORTED OR TESTED BY HARMONIC.
#       USE IT AT YOUR OWN RISK !!!!
# Author: John Vasconcelos
# Date: 10/02/2017
# Version 1.1
###########################################################

'''Example command:
./vos_migrate_services.py --rt_from vosdashboard.dfwcpcpurple.pod1.ds.dtvops.net --rt_to vosdashboard.dfwcpcpurple.pod3.ds.dtvops.net 
 --serv_file serv-f.txt --src_file src-f.txt --ats_file dest-f.txt --blackout_img http://myblackoutimage.com/img.png --sigloss_img http://signalossimage.com/img.png

'''

# vos.py needs to be in the same path as this script.
import vos
import sys
import argparse
import os
import json
import vos
import time
import getpass
import yaml
import uuid
import datetime


#Logfile Name Construction
now = datetime.datetime.now()
log_file = 'vos-migration-' + now.strftime("%Y-%m-%d-%H%M") + '.log'

def check_image_exists(imgurl,imgs):

    img_id = ""
    for img in imgs:
        if imgurl == img['url']:
            img_id = img['id']
            vos.log_write("INFO","Image URL %s ID: %s Already Exists and will not be Created" %(imgurl,img_id),log_file)

    return img_id

def create_image(imgurl,vosrt,vos_session):

    img_id = str(uuid.uuid4())

    param = json.dumps({'id':img_id, 'url':imgurl})

    ret = vos.vos_add_image(param,vosrt,vos_session)

    if ret.status_code == 200:
        vos.log_write("INFO","Image URL %s ID: %s Created Successfully" %(imgurl,img_id),log_file)
        vos.log_write("INFO","\n %s \n" %vos_ret.text,log_file)
        return img_id
    else:
        vos.log_write("ERROR","Image URL %s failed to create... ABORTING SCRIPT !!!" % imgurl ,log_file)
        vos.log_write("ERROR","\n %s \n" %vos_ret,log_file)
        vos.log_write("ERROR","\n %s \n" %vos_ret.text,log_file)
        sys.exit(2)

def check_cl_file(clfile,iname):
    
    cl = ""
    for item in clfile:
        item_name = item.split(',')[0]

        if iname == item_name:
            cl = item.split(',')[1].strip()
    clfile.seek(0) 

    return cl


def create_source(srctxt,clgrpid,siglossid,vosrt,vos_session):

    src_yaml = yaml.safe_load(srctxt)

    n = 0
    for src_input in src_yaml['inputs']:
        if src_input['type'] == "ZIXI":
            src_yaml['inputs'][n]['zixiSettings']['harmonicUplinkSetting']['uplinkGroupId'] = clgrpid
        if src_input['type'] == "SLATE":
            src_yaml['inputs'][n]['slateSettings']['imageId'] = siglossid
        n += 1

    param = json.dumps(src_yaml)

    vos_ret = vos.vos_add_source(param,vosrt,vos_session)

    if vos_ret.status_code == 200:
        vos.log_write("INFO","Source %s ID: %s Created Successfully" %(src_yaml['name'],src_yaml['id']),log_file)
        vos.log_write("INFO","\n %s \n" %vos_ret.text,log_file)
        ret = True
    else:
        vos.log_write("ERROR","Source %s ID: %s FAILED TO CREATE !!!" %(src_yaml['name'],src_yaml['id']),log_file)
        vos.log_write("ERROR","\n %s \n" %vos_ret,log_file)
        vos.log_write("ERROR","\n %s \n" %vos_ret.text,log_file)
        ret = False

    return ret


def create_dest(dsttxt,clgrpid="",vosrt="",vos_session=""):

    dst_yaml = yaml.safe_load(dsttxt)

    if clgrpid:
        dst_yaml['outputs'][0]['ipSettings']['cloudlinkGroupId'] = clgrpid

    param = json.dumps(dst_yaml)

    vos_ret = vos.vos_add_destination(param,vosrt,vos_session)

    if vos_ret.status_code == 200:
        vos.log_write("INFO","Destination %s ID: %s Created Successfully" %(dst_yaml['name'],dst_yaml['id']),log_file)
        vos.log_write("INFO","\n %s \n" %vos_ret.text,log_file)
        ret = True
    else:
        vos.log_write("ERROR","Destination %s ID: %s FAILED TO CREATE !!!" %(dst_yaml['name'],dst_yaml['id']),log_file)
        vos.log_write("ERROR","\n %s \n" %vos_ret,log_file)
        vos.log_write("ERROR","\n %s \n" %vos_ret.text,log_file)
        ret = False

    return ret


def create_serv(srvtxt,src_ids,dst_ids,blackout_id,vosrt,vos_session):

    srv_yaml = yaml.safe_load(srvtxt)

    print srv_yaml

    srv_yaml[0]['serviceSources'] = []
    for src in src_ids:
        srv_yaml[0]['serviceSources'].append({'sourceId':src[0],'rank':src[1]})
    
    
    srv_yaml[0]['destinationId'] = dst_ids[0]

    srv_yaml[0]['destinationsId'] = dst_ids


    if srv_yaml[0]['addons']:
        srv_yaml[0]['addons']['scte35SlateAddon']['imageId'] = blackout_id


    param = json.dumps(srv_yaml[0])

    vos_ret = vos.vos_service_add(param,vosrt,vos_session)

    

    if vos_ret.status_code == 200:
        vos.log_write("INFO","Service %s ID: %s Created Successfully" %(srv_yaml[0]['name'],srv_yaml[0]['id']),log_file)
        vos.log_write("INFO","\n %s \n" %vos_ret.text,log_file)
        ret = True
    else:
        vos.log_write("ERROR","Service %s ID: %s FAILED TO CREATE !!!" %(srv_yaml[0]['name'],srv_yaml[0]['id']),log_file)
        vos.log_write("ERROR","\n %s \n" %vos_ret,log_file)
        vos.log_write("ERROR","\n %s \n" %vos_ret.text,log_file)
        ret = False

    return ret




def main(argv):
    parser = argparse.ArgumentParser(description='***VOS Service Migration***', epilog = 'Usage example:\n'+sys.argv[0]+' --cloud_url=https://hkvpurple-01.nebula.video --cloud_username=USERNAME', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--rt_from', dest='rt_from', action='store', help='RT from where to export Configuration.', required=True)
    parser.add_argument('--rt_to', dest='rt_to', action='store', help='RT where to import Configuration into.', required=True)
    parser.add_argument('--serv_file', dest='serv_file', action='store', help='Batch File with services to be migrated.', required=True)
    parser.add_argument('--src_file', dest='src_file', action='store', help='Batch File with Source - Cloudlink assignmet on the Destination RT', required=True)
    parser.add_argument('--ats_file', dest='ats_file', action='store', help='Batch File with Destination - Cloudlink assignmet on the Destination RT', required=True)
    parser.add_argument('--blackout_img', dest='blackout_img', action='store', help='Blackout Slate URL for Services', required=True)
    parser.add_argument('--sigloss_img', dest='sigloss_img', action='store', help='Signal Loss Slate URL for Sources', required=True)


    args = parser.parse_args()

    rt_to = args.rt_to

    rt_from = args.rt_from

    blackout_img = args.blackout_img

    sigloss_img = args.sigloss_img

    #Checks if file exists
    if not os.path.isfile(args.serv_file):
        print "File %s does not exist !!" %args.serv_file
        sys.exit(2)

    #Checks if file exists
    if not os.path.isfile(args.src_file):
        print "File %s does not exist !!" %args.src_file
        sys.exit(2)

    #Checks if file exists
    if not os.path.isfile(args.ats_file):
        print "File %s does not exist !!" %args.ats_file
        sys.exit(2)    

    #Open Files
    srv_f = open(args.serv_file)

    src_f = open(args.src_file)

    dst_f = open(args.ats_file)


    print "\nScript will Migrate the Services, Sources and Destinations\n"

    print "FROM RT: %s\n" %rt_from

    print "TO RT: %s\n" %rt_to

    for item in srv_f:
        print item

    print "\nScript will Migrate the Services, Sources and Destinations\n"

    print "FROM RT: %s\n" %rt_from

    print "TO RT: %s\n" %rt_to

    #Checks if Parameters are correct
    while True:

        m_continue = raw_input("IS THE INFORMATION ABOVE CORRECT? CONTINUE WITH MIGRATION ? (Y/N) : ")

        if m_continue.lower() not in ('y' , 'n'):
            print "Answer not valid. Please enter Y or N !"
            continue
        else:
            break

    if m_continue.lower() == "n":
        print "Script has been Aborted"
        sys.exit(2)

    srv_f.seek(0)

    #Creates VOS Requests Session. It will prompt for user and password. 
    vos_session = vos.vos_get_session()

    # Loads variable with json with all images on the Destination RT
    imgs = vos.vos_get_image_all(rt_to,vos_session).json()
    
    sigloss_id = check_image_exists(sigloss_img,imgs)
    blackout_id = check_image_exists(blackout_img,imgs)

    #Creates signall loss image
    if not sigloss_id:
        
        sigloss_id = create_image(sigloss_img,rt_to,vos_session)


    #Creates blackout image
    if not blackout_id:
        blackout_id = create_image(blackout_img,rt_to,vos_session)


    servs = vos.vos_get_service_all(rt_from,vos_session)

    cls_to = vos.vos_get_cl_list(rt_to,vos_session)

    if servs.status_code == 200:

        for srv in servs.json():

            srv_name = srv['name']
            
            for item in srv_f:
                if item.strip() == srv_name:

                    vos.log_write("INFO","Processing Service: %s" %srv['name'],log_file) 

                    if vos.vos_get_service_name(srv_name,rt_to,vos_session).json():

                        vos.log_write("INFO","Service %s already exists in RT %s. Skipping the processing for service.\n" %(srv_name,rt_to),log_file)
                        break
                    
                    #Processing sources
                    src_ids = []
                    src_processed = True
                    for src in srv['serviceSources']:
                        src_from = vos.vos_get_source_id(src['sourceId'],rt_from,vos_session)
                        src_to = vos.vos_get_source_name(src_from.json()['name'],rt_to,vos_session).json()
                        if not src_to:
                            src_cl = check_cl_file(src_f,src_from.json()['name'])
                            if not src_cl:
                                vos.log_write("ERROR","Source to Cloudlink Assignment not available on file %s" %args.src_file,log_file)
                                src_processed = False
                                break
                            
                            cl_grpid = vos.vos_get_clgrp_id_from_name(src_cl,rt_to,vos_session)

                            if not cl_grpid:
                                vos.log_write("ERROR","Cloudlink %s assigned for Source %s does not exist in the Destination RT. Aborting Service %s Configuration !" %(src_cl,src_from.json()['name'],srv_name),log_file)
                                src_processed = False
                                break                            

                            print "Creating Source...."
                            if not create_source(src_from.text,cl_grpid,sigloss_id,rt_to,vos_session):
                                vos.log_write("ERROR","Source %s could not be Created. Aborting Service %s Creation!!!" %(src_from.json()['name'],srv_name),log_file) 
                                src_processed = False
                                break

                            src_ids.append([src['sourceId'],src['rank']])
                        else:
                            src_ids.append([src_to[0]['id'],src['rank']])

                    # Stop Processing the Service if any error Occurs.
                    if not src_processed:
                        vos.log_write("ERROR","Service %s Could not be Processed due to Errors Above" %srv_name,log_file)
                        break                       

                    #Processing Destinations
                    dst_ids = []
                    dst_processed = True
                    for dst in srv['destinationsId']:
                        dst_from = vos.vos_get_destination_id(dst,rt_from,vos_session)
                        dst_to = vos.vos_get_destination_name(dst_from.json()['name'],rt_to,vos_session).json()
                        
                        if not dst_to:
                            if dst_from.json()['type'] == "ATS":
                                dst_cl = check_cl_file(dst_f,dst_from.json()['name'])
                                if not dst_cl:
                                    vos.log_write("ERROR","Destination to Cloudlink Assignment not available on file %s" %args.ats_file,log_file)
                                    dst_processed = False
                                    break

                                cl_grpid = vos.vos_get_clgrp_id_from_name(dst_cl,rt_to,vos_session)

                                if not cl_grpid:
                                    vos.log_write("ERROR","Cloudlink %s assigned for Destination %s does not exist in the Destination RT. Aborting Service %s Configuration !" %(dst_cl,dst_from.json()['name'],srv_name),log_file)
                                    dst_processed = False
                                    break     

                                if not create_dest(dst_from.text,cl_grpid,rt_to,vos_session):
                                    vos.log_write("ERROR","Destination %s could not be Created. Aborting Service %s Creation!!!" %(dst_from.json()['name'],srv_name),log_file) 
                                    dst_processed = False
                                    break

                                dst_ids.append(dst_from.json()['id'])
                            else:
                                if not create_dest(dst_from.text,"",rt_to,vos_session):
                                    vos.log_write("ERROR","Destination %s could not be Created. Aborting Service %s Creation!!!" %(dst_from.json()['name'],srv_name),log_file) 
                                    dst_processed = False
                                    break

                                dst_ids.append(dst_from.json()['id'])

                        else:
                            dst_ids.append(dst_to[0]['id'])                          

    
                    # Stop Processing the Service if any error Occurs.
                    if not dst_processed:
                        vos.log_write("ERROR","Service %s Could not be Processed due to Errors Above" %srv_name,log_file)
                        break   
    
                    #Create Service
                    srv_from = vos.vos_get_service_name(srv_name,rt_from,vos_session)

                    if not create_serv(srv_from.text,src_ids,dst_ids,blackout_id,rt_to,vos_session):
                        vos.log_write("ERROR","Service %s Could not be Created. Check log file %s for detail" %(srv_name,log_file),log_file)



            srv_f.seek(0)




if __name__ == "__main__":
    main(sys.argv[1:])