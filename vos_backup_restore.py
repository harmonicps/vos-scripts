#!/usr/bin/env python


###########################################################
# Script: vos_backup_restore.py
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
import time
import yaml
import datetime


#Logfile Name Construction
now = datetime.datetime.now()
log_file = 'vos-backup-restore-' + now.strftime("%Y-%m-%d-%H%M") + '.log'


def check_status(vos_ret,config,config_name,config_id):

    if vos_ret.status_code == 200:
        vos.log_write("INFO","%s %s ID: %s Created Successfully" %(config,config_name,config_id),log_file)
        vos.log_write("INFO","\n %s \n" %vos_ret.text,log_file)
    else:
        vos.log_write("ERROR","%s %s failed to create... ABORTING SCRIPT !!!" %(config,config_name) ,log_file)
        vos.log_write("ERROR","\n %s \n" %vos_ret,log_file)
        vos.log_write("ERROR","\n %s \n" %vos_ret.text,log_file)
        sys.exit(2)


def main(argv):
    parser = argparse.ArgumentParser(description='***VOS Service Migration***', epilog = 'Usage example:\n'+sys.argv[0]+' --cloud_url=https://hkvpurple-01.nebula.video --cloud_username=USERNAME', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--cloud_url', dest='cloud_url', action='store', help='RT from where to export Configuration.', required=False)
    parser.add_argument('--srv_file', dest='srv_file', action='store', help='JSON File for Services', required=False)
    parser.add_argument('--src_file', dest='src_file', action='store', help='JSON File for Sources', required=False)
    parser.add_argument('--dst_file', dest='dst_file', action='store', help='JSON File for Destinations', required=False)
    parser.add_argument('--img_file', dest='img_file', action='store', help='JSON File for Images', required=False)
    parser.add_argument('--drm_file', dest='drm_file', action='store', help='JSON File for DRM Systems/Settings', required=False)
    parser.add_argument('--backup', dest='backup', action='store_true', help='Backup Configuration', required=False)
    parser.add_argument('--restore', dest='restore', action='store_true', help='Restore Configuration', required=False)
    parser.add_argument('--srv_off', dest='srv_off', action='store_true', help='Restore with Service Offline', required=False)


    args = parser.parse_args()

    

    if args.backup and args.restore:
        print "Please use either --backup or --restore but not both :-)"
        sys.exit(2)


    #Creates VOS Requests Session. It will prompt for user and password.
    vos_session = vos.vos_get_session()

    vosrt = args.cloud_url

    # Backup Configuration
    if args.backup:


        #Backup Sources
        f_src = open(args.src_file,'w')

        vos_srcs = vos.vos_get_source_all(vosrt,vos_session)

        json.dump(vos_srcs.json(),f_src)

        f_src.close()

        #Backup Destinations
        f_dst = open(args.dst_file,'w')

        vos_dsts = vos.vos_get_destination_all(vosrt,vos_session)

        json.dump(vos_dsts.json(),f_dst)

        f_dst.close()

        #Backup Services
        f_srv = open(args.srv_file,'w')

        vos_srvs = vos.vos_get_service_all(vosrt,vos_session)

        json.dump(vos_srvs.json(),f_srv)

        f_srv.close()

        #Backup Images
        f_img = open(args.img_file,'w')

        vos_imgs = vos.vos_get_image_all(vosrt,vos_session)

        json.dump(vos_imgs.json(),f_img)

        f_img.close()

        #Backup DRM Systems
        if args.drm_file:
            f_drm = open(args.drm_file,'w')

            vos_drms = vos.vos_get_drmsys_all(vosrt,vos_session)

            json.dump(vos_drms.json(),f_drm)

            f_drm.close()
            
            #Backup DRM Settings
            drm_sets_file = args.drm_file + '_settings'
            
            f_drm_sets = open(drm_sets_file,'w')

            vos_drm_sets = vos.vos_get_drm_settings(vosrt,vos_session)

            json.dump(vos_drm_sets.json(),f_drm_sets)

            f_drm_sets.close()

    
    #Restores Configuration
    if args.restore:             
        
        #Restores DRM Configuration
        if args.drm_file:

            #Checks if file exists
            if not os.path.isfile(args.drm_file):
                print "File %s does not exist !!" %args.drm_file
                sys.exit(2)            

            #Restores DRM Settings
            drm_sets_file = args.drm_file + '_settings'

            #Checks if file exists
            if not os.path.isfile(drm_sets_file):
                print "File %s does not exist !!" %drm_sets_file
                sys.exit(2)

            with open(args.drm_file) as drm_data:
                drm = yaml.safe_load(drm_data)
    
            for drm_item in drm:

                param = json.dumps(drm_item)
                
                vos_ret = vos.vos_drmsys_add(param,vosrt,vos_session)

                check_status(vos_ret,"DRM System",drm_item['name'],drm_item['id'])

            with open(drm_sets_file) as drm_set:
                for param in drm_set:
                    vos_ret = vos.vos_mod_drm_settings(param,vosrt,vos_session)
                    if not vos_ret.status_code == 200:
                        vos.log_write("ERROR","Failed to Update DRM Settings with the following settings:\n%s" %param ,log_file)

        #Restore Images
        if args.img_file:
            #Checks if file exists
            if not os.path.isfile(args.img_file):
                print "File %s does not exist !!" %args.img_file
                sys.exit(2)       
    
            with open(args.img_file) as img_data:
                i = yaml.safe_load(img_data)
    
            for img_item in i:
    
                param = json.dumps(img_item)
                
                vos_ret = vos.vos_add_image(param,vosrt,vos_session)
    
                check_status(vos_ret,"Image",img_item['url'],img_item['id'])


        #Restore Sources

        if args.src_file:
    
            #Checks if file exists
            if not os.path.isfile(args.src_file):
                print "File %s does not exist !!" %args.src_file
                sys.exit(2)

            with open(args.src_file) as src_data:
                s = yaml.safe_load(src_data)
    
            for src_item in s:
    
                param = json.dumps(src_item)
                
                vos_ret = vos.vos_add_source(param,vosrt,vos_session)
    
                check_status(vos_ret,"Source",src_item['name'],src_item['id'])
    
                time.sleep(4)
    

        #Restore Destinations
        if args.dst_file:
    
            #Checks if file exists
            if not os.path.isfile(args.dst_file):
                print "File %s does not exist !!" %args.dst_file
                sys.exit(2)
        
            with open(args.dst_file) as dst_data:
                d = yaml.safe_load(dst_data)
    
            for dst_item in d:
    
                param = json.dumps(dst_item)
                
                vos_ret = vos.vos_add_destination(param,vosrt,vos_session)
    
                check_status(vos_ret,"Destination",dst_item['name'],dst_item['id'])
    
                time.sleep(4)

        #Restore Services
        
        if args.srv_file:
            #Checks if file exists
            if not os.path.isfile(args.srv_file):
                print "File %s does not exist !!" %args.srv_file
                sys.exit(2)
           
    
            with open(args.srv_file) as srv_data:
                sv = yaml.safe_load(srv_data)
    
            for srv_item in sv:
                if args.srv_off:
                    srv_item['controlState'] = "OFF"
                param = json.dumps(srv_item)
                
                vos_ret = vos.vos_service_add(param,vosrt,vos_session)
    
                check_status(vos_ret,"Service",srv_item['name'],srv_item['id'])
    
                time.sleep(10)




if __name__ == "__main__":
    main(sys.argv[1:])