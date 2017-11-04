#!/usr/bin/env python


###########################################################
# Script: vos_source_helper.py
# NOTE: THIS SCRIPT IS NOT SUPPORTED OR TESTED BY HARMONIC.
#       USE IT AT YOUR OWN RISK !!!!
# Author: John Vasconcelos
# Date: 06/05/2017
# Version 1.1
###########################################################

# vos.py needs to be in the same path as this script.
import vos
import sys
import argparse
import os
import getpass
import yaml, json
import uuid
import time
from pprint import pprint

def main(argv):
    parser = argparse.ArgumentParser(description='***VOS Source Helper***', epilog = 'Usage example:\n'+sys.argv[0]+' --cloud_url <RT URL> --export --file=sources.txt', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--cloud_url', dest='cloud_url', action='store', help='Cloud url', required=True)
    parser.add_argument('--cloud_username', dest='cloud_username', action='store', default='', help='Cloudlink username', required=False)
    parser.add_argument('--file', dest='src_file', action='store', help='Batch File with services to be processed.', required=False)
    parser.add_argument('--src_list_file', dest='src_list_file', action='store', help='List of Sources to be Processed', required=False)
    parser.add_argument('--cl_file', dest='cl_file', action='store', help='Source to CL Association File', required=False)
    parser.add_argument('--cloud_link', dest='cloud_link', action='store', default='', help='Cloudlink Name', required=False)
    parser.add_argument('--import', dest='import_src', action='store_true', help='Import Sources from a File', required=False)
    parser.add_argument('--export', dest='export_src', action='store_true', help='Export Sources to a File', required=False)
    parser.add_argument('--associate_cl', dest='ass_cl', action='store_true', help='Associate CL to Source based on a File', required=False)
    parser.add_argument('--set_audio_label', dest='set_audio_label', action='store_true', help='Set the Audio Label', required=False)
    parser.add_argument('--set-options', dest='set_opt', action='store_true', help='Set Other Misc. Options', required=False)



    args = parser.parse_args()

    if args.import_src and args.export_src:
        print "Pick Either --import or --export, but not Both. :-)"
        sys.exit(2)

    if not args.import_src and not args.export_src and not args.ass_cl and not args.set_opt and not args.set_audio_label:
        print "Specify either --import or --export option or --associate_cl"
        sys.exit(2)

    if not args.cloud_username:
        user = raw_input("Enter the Username for VOS:\n")
    else:
        user = args.cloud_username

    passwd = getpass.getpass("Enter the Password:\n")

    vos_session = vos.vos_get_session(user,passwd)

    vosrt = args.cloud_url

    cl_id = ""

    source_list = []

    if args.import_src:

        if not os.path.isfile(args.src_file):
            print "File %s does not exist !!" %args.src_file
            sys.exit(2)

        f = open(args.src_file)

        src_json = json.load(f)


        if not args.cl_file:
            # raw_input returns the empty string for "enter"
            yes = set(['yes','y', 'ye', ''])
            no = set(['no','n'])

            choice = raw_input("--cl_file option not specified. Sources will be Imported with the CL on json file. Continue ?" ).lower()
            if choice in yes:
                pass
            elif choice in no:
                sys.exit(2)
            else:
                sys.stdout.write("Please respond with 'yes' or 'no'")



        for src in src_json:

            src_new_id = str(uuid.uuid4())

            src['id'] = src_new_id

            if args.cl_file:

                if not os.path.isfile(args.cl_file):
                    print "File %s does not exist !!" %args.cl_file
                    sys.exit(2)

                clf = open(args.cl_file)

                for srccl in clf:

                    srcname = srccl.split(",")[0]
                    clname = srccl.split(",")[1]
                    if srcname.strip() == src['name']:
                        cl_list = vos.vos_get_cl_list(vosrt,vos_session)
                        for cl in cl_list:
                            if clname.strip() == cl['clname']:
                                src['inputs'][0]['zixiSettings']['harmonicUplinkSetting']['uplinkGroupId'] = cl['clgroup']


            param = json.dumps(src)

            #print param
            #print "\n"

            print vos.vos_add_source(param,vosrt,vos_session)


    if args.export_src:

        if args.src_list_file:
            if not os.path.isfile(args.src_list_file):
                print "File %s does not exist !!" %args.src_list_file
                sys.exit(2)

            slf = open(args.src_list_file)

        f = open(args.src_file,'w')

        srcs = vos.vos_get_source_all(vosrt,vos_session).json()

        if args.cloud_link:

            cl_list = vos.vos_get_cl_list(vosrt,vos_session)
            for cl in cl_list:
                if args.cloud_link == cl['clname']:
                    cl_id = cl['clgroup']

            if not cl_id:
                print "Cloudlink does not Exist on this system !"
                sys.exit(2)

        

        for src in srcs:

            if cl_id:
                if src['inputs'][0]['zixiSettings']['harmonicUplinkSetting']['uplinkGroupId'] == cl_id:
                    print "Exporting service: %s\n" %src['name']
                    source_list.append(src)
            elif args.src_list_file:

                for src_exp in slf:
                    if src['name'] == src_exp.strip():
                        print "Exporting service: %s\n" %src['name']
                        source_list.append(src)

            else:
                print "Exporting service: %s\n" %src['name']
                source_list.append(src)

        json.dump(source_list, f)

        f.close()

    if args.ass_cl:

        if args.cl_file:
            if not os.path.isfile(args.cl_file):
                print "File %s does not exist !!" %args.cl_file
                sys.exit(2)

            clf = open(args.cl_file)
        else:
            print "You need to specify the option --associate_cl"
            sys.exit(2)



        for srccl in clf:

            srcname = srccl.split(",")[0]
            clname = srccl.split(",")[1]
           #print srcname.strip()
            src = vos.vos_get_source_name(srcname.strip(),vosrt,vos_session)
           # print src.json()

            srcy = yaml.safe_load(src.text)
            #print srcy
            #print"\n\n\n\n"

            if srcname.strip() == srcy[0]['name']:
                cl_list = vos.vos_get_cl_list(vosrt,vos_session)
                for cl in cl_list:
                    if clname.strip() == cl['clname']:
                        srcy[0]['inputs'][0]['zixiSettings']['harmonicUplinkSetting']['uplinkGroupId'] = cl['clgroup']

                param = json.dumps(srcy[0])

                print vos.vos_add_source(param,vosrt,vos_session)


    if args.set_opt:

        srcs = vos.vos_get_source_all(vosrt,vos_session)

        srcsy = yaml.safe_load(srcs.text)

        for sr_opt in srcsy:

            print sr_opt['id']
            print "\n"

            is_default = False

            index = 0
            
            '''
            if sr_opt['inputs'][0]['zixiSettings']['grooming']:

                for aud_gr in sr_opt['inputs'][0]['zixiSettings']['grooming']['audioGrooming']['tracks']:

                    if aud_gr['isDefault'] and sr_opt['inputs'][0]['zixiSettings']['grooming']['audioGrooming']['tracks'][index]['hasNielsenWatermark'] == False:
                        sr_opt['inputs'][0]['zixiSettings']['grooming']['audioGrooming']['tracks'][index]['hasNielsenWatermark'] = True
                        is_default = True

                    index += 1

                if not is_default:
                    sr_opt['inputs'][0]['zixiSettings']['grooming']['audioGrooming']['tracks'][0]['isDefault'] = True
                    sr_opt['inputs'][0]['zixiSettings']['grooming']['audioGrooming']['tracks'][0]['hasNielsenWatermark'] = True
            '''

            if not sr_opt['inputs'][1]['slateSettings']:
                sr_opt['inputs'][1]['slateSettings'] = {"type": "SIGNAL_LOSS","imageId": "db6c9c17-0adf-5fbf-9db9-8c319b3be36f","customSlateSettings": None}

            if not sr_opt['inputs'][1]['slateSettings']['imageId'] == "db6c9c17-0adf-5fbf-9db9-8c319b3be36f":

                sr_opt['inputs'][1]['slateSettings']['imageId'] = "db6c9c17-0adf-5fbf-9db9-8c319b3be36f"

            param = json.dumps(sr_opt)

            print vos.vos_mod_source(sr_opt['id'],param,vosrt,vos_session)

            time.sleep(10)


    if args.set_audio_label:

        srcs = vos.vos_get_source_all(vosrt,vos_session)

        srcsy = yaml.safe_load(srcs.text)

        for sr_opt in srcsy:

            print sr_opt['id']
            print "\n"

            aud_label = 1
            index = 0

            for audio in sr_opt['inputs'][0]['zixiSettings']['grooming']['audioGrooming']['tracks']:
                
                if not audio['labels']:
                    sr_opt['inputs'][0]['zixiSettings']['grooming']['audioGrooming']['tracks'][index]['labels'] = ["audio_" + str(aud_label)]

                aud_label += 1
                index += 1


            param = json.dumps(sr_opt)

            print param

            #print vos.vos_mod_source(sr_opt['id'],param,vosrt,vos_session)

            time.sleep(10)


if __name__ == "__main__":
    main(sys.argv[1:])
