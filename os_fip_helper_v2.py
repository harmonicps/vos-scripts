#!/bin/env python
import json
import os
import re
import sys
import csv

# For OpenStack
from keystoneauth1 import loading as ks_loading
from keystoneauth1 import session as ks_session
# from neutronclient.v2_0 import client as neutron_client
from novaclient import client as nova_client
import argparse
from collections import defaultdict

class ObjectWrapper(object):
    def __init__(self, in_item):
        for key, value in in_item.iteritems():
            if isinstance(value, (list, tuple)):
               setattr(self, key, [ObjectWrapper(x) if isinstance(x, dict) else x for x in value])
            else:
               setattr(self, key, ObjectWrapper(value) if isinstance(value, dict) else value)

class FIPHelper(object):
    def __init__(self, argv):
        # Intialize member variables
        self.nova_client = None
        # self.neutron_client = None

        self.name = argv[0] if (argv is not None) else "FIPHelper"

        # Parse input OpenStack environment variables
        self.os_username     = os.environ.get('OS_USERNAME')
        self.os_password     = os.environ.get('OS_PASSWORD')
        self.os_auth_url     = os.environ.get('OS_AUTH_URL')
        self.os_project_name = os.environ.get('OS_PROJECT_NAME')
        self.os_tenant_id    = os.environ.get('OS_TENANT_ID')
        self.os_tenant_name  = os.environ.get('OS_TENANT_NAME')
        self.os_bypass_url   = os.environ.get('NOVACLIENT_BYPASS_URL')

        # Sanity check
        if len(argv) < 2 or argv[1] == "-h" or argv[1] == "--help": # or (argv[1] != "allocate" and argv[1] != "associate"):
            self._usage()
            raise RuntimeError("Missing input arguments!")

        if (self.os_username is None) or (self.os_password is None) or (self.os_auth_url is None) or (self.os_project_name is None):
            print("Missing environment variables from OpenStack RC file!")
            print("You should source related OpenStack RC file before running the script.")
            raise RuntimeError("Missing environment variables from OpenStack RC file!")

    def _usage(self):
        print('Usage: <command>')
        print('allocate <pool_ingress> <#ingress> <pool_egress> <#egress>')
        print('associate <stack_name> <ips_list_file>')
        print('reassign <floating_ip> <new_node_private_ip>')

    def _get_nova_client(self):
        '''
            adopt Sessionclient implementation, which is the original code for accessible service catalog
        '''

        if self.nova_client is None:
            loader = ks_loading.get_plugin_loader('password')
            auth = loader.load_from_options(auth_url=self.os_auth_url,
                                            username=self.os_username,
                                            password=self.os_password,
                                            project_name=self.os_project_name
)
            try:
                sess = ks_session.Session(auth=auth, verify=False)
                self.nova_client = nova_client.Client("2", session=sess)
            except:
              raise
        '''
            adopt HTTPclient implementation to create Client, so as to supply bypass_url
        '''
        # if self.nova_client is None:
        #     try:
        #         self.nova_client = nova_client.Client("2", auth_url=self.os_auth_url,
        #                                                 username=self.os_username,
        #                                                 password=self.os_password,
        #                                                 project_name=self.os_project_name,
        #                                                 tenant_id=self.os_tenant_id,
        #                                                 insecure=True,
        #                                                 bypass_url=self.os_bypass_url)
        #     except:
        #         raise

    # def _get_neutron_client(self):
    #     if self.neutron_client is None:
    #         loader = ks_loading.get_plugin_loader('password')
    #         auth = loader.load_from_options(auth_url=self.os_auth_url,
    #                                         username=self.os_username,
    #                                         password=self.os_password,
    #                                         project_name=self.os_project_name)
    #         sess = ks_session.Session(auth=auth)
    #         self.neutron_client = neutron_client.Client(session=sess)

    def list_stack_vms(self, nova_client, stack_name=None):
        vm_list = []
        if stack_name is not None:
            tmp_vm_list = nova_client.servers.list()
            for i,vm in enumerate(tmp_vm_list):
                if 'stack_name' in vm.metadata.keys() and vm.metadata['stack_name'] == stack_name:
                    vm_list.append(vm)
        else:
            vm_list = nova_client.servers.list()
        return vm_list

    def list_stack_ingress_vms(self, nova_client, stack_name):
        vm_list = []
        #tmp_vm_list = nova_client.servers.list(search_opts={'metadata': '[{"stack_name": "%s"}, {"vos_roles": "live_ingest"}]' % (stack_name)})
        tmp_vm_list = nova_client.servers.list()
        for i,vm in enumerate(tmp_vm_list):
            if 'stack_name' in vm.metadata.keys() and vm.metadata['stack_name'] == stack_name:
                if 'vos_roles' in vm.metadata.keys() and vm.metadata['vos_roles'] == "live_ingest":
                    vm_list.append(vm)
        return vm_list

    def list_stack_egress_vms(self, nova_client, stack_name=None):
        vm_list = []
        #tmp_vm_list = nova_client.servers.list(search_opts={'metadata': '[{"stack_name": "%s"}, {"vos_roles": "egress"}]' % (stack_name)})
        tmp_vm_list = nova_client.servers.list()
        for i,vm in enumerate(tmp_vm_list):
            if 'stack_name' in vm.metadata.keys() and vm.metadata['stack_name'] == stack_name:
                if 'vos_roles' in vm.metadata.keys() and vm.metadata['vos_roles'] == "egress":
                    vm_list.append(vm)
        return vm_list

    # def list_ports(self, neutron_client):
    #     port_list = None
    #     ret_dict = self.neutron_client.list_ports()
    #     if ret_dict is not None:
    #         port_list = ObjectWrapper(ret_dict).ports
    #     return port_list

    # def list_floating_ips(self, neutron_client):
    #     floating_ip_list = None
    #     ret_dict = self.neutron_client.list_floatingips()
    #     if ret_dict is not None:
    #         floating_ip_list = ObjectWrapper(ret_dict).floatingips
    #     return floating_ip_list

    def list_floating_ips(self, nova_client):
        floating_ip_list = None
        floating_ip_list = nova_client.floating_ips.list()
        return floating_ip_list

    def create_floating_ips(self, nova_client, pool, num):
        ips_list = []
        for i in range(0,num):
            ips_list.append(nova_client.floating_ips.create(pool).ip)
        return ips_list

    def map_vm_floating_ip(self, vm_list, floating_ip_list):
        vm_fip_dict = {}
        vm_id_list = [ vm.id for vm in vm_list ]

        # Iterate list of floating IP
        for floating_ip in floating_ip_list:
            # Check if the floating IP blongs to our VM
            if floating_ip.instance_id in vm_id_list:
                # Insert the entry on private IP for sorting
                vm_fip_dict[floating_ip.fixed_ip] = ObjectWrapper({ "vm": floating_ip.instance_id, "floating_ip": floating_ip.ip })

        return vm_fip_dict

    def deassociate_fip(self, fip, nova_client):
        print "start to deassociate floating ip %s" % fip
        nodes = nova_client.servers.list()
        for node in nodes:
            node_ip_dict = nova_client.servers.ips(node)
            print node_ip_dict
            if len(node_ip_dict.values()) > 0:
                node_ip_list = node_ip_dict.values()[0]
                if isinstance(node_ip_list, list):
                    for node_ip in node_ip_list:
                        if fip in node_ip.values():
                            print fip, "located"
                            nova_client.servers.remove_floating_ip(node, fip)
                            return

    def reassign_fip(self, fip, new_node, nova_client):
        print "start to reassign floating ip"
        nodes = nova_client.servers.list()
        for node in nodes:
            node_ip_dict = nova_client.servers.ips(node)
            if len(node_ip_dict.values()) > 0:
                node_ip_list = node_ip_dict.values()[0]
                if isinstance(node_ip_list, list):
                    for node_ip in node_ip_list:
                        if new_node in node_ip.values():
                            print new_node, "located"
                            nova_client.servers.add_floating_ip(node, fip)
                            return

    def reboot_server(self, reboot_type, private_ip, nova_client):
        nodes = nova_client.servers.list()
        for node in nodes:
            node_in_dict = node.to_dict()
            node_ip_list = node_in_dict["addresses"].values()[0]
            if isinstance(node_ip_list, list):
                for node_ip in node_ip_list:
                    if private_ip in node_ip.values():
                        print private_ip, "located as", node_in_dict["name"], node_in_dict["status"]
                        print "now start to perform", reboot_type, "reboot"
                        nova_client.servers.reboot(node, reboot_type)
                        print "now complete performing", reboot_type, "reboot"


    def main(self, argv):
        #print('Starting OpenStack VOS cluster floating IP helper ...')
        #print('   > Stack Name: %s' % (self.stack_name))

        self._get_nova_client()

        if argv[1] == 'allocate':
            ips_ingress = []
            ips_egress = []
            pool_ingress = argv[2]
            num_ingress = int(argv[3])
            pool_egress = argv[4]
            num_egress = int(argv[5])
            ips_ingress = self.create_floating_ips(self.nova_client, pool_ingress, num_ingress)
            for i, val in enumerate(ips_ingress):
                print 'ingress,'+val
            ips_egress = self.create_floating_ips(self.nova_client, pool_egress, num_egress)
            for i, val in enumerate(ips_egress):
                print 'egress,'+val
        elif argv[1] == 'associate':
            stack_name = argv[2]
            ips_list_file = argv[3]
            if not os.path.isfile(ips_list_file):
                print "Error: File "+ips_list_file+" not exist"
                exit(1)

            # reconstruct ips list from file
            ips_ingress_list = []
            ips_egress_list = []
            with open(ips_list_file) as csv_file:
                for row in csv.reader(csv_file, delimiter=','):
                  if row[0] == 'ingress':
                      ips_ingress_list.append(row[1])
                  elif row[0] == 'egress':
                      ips_egress_list.append(row[1])

            # build the map of instance already having fip
            fip_map = dict()
            fip_list = self.list_floating_ips(self.nova_client)
            for i,val in enumerate(fip_list):
                fip_map[val.instance_id] = val


            #print self.list_stack_vms(self.nova_client, stack_name)
            #exit(1)

            for x in range(0,2):
                # find out the VM not yet associated with fip under the stack
                vms_map = defaultdict(list)
                if x == 0:
                    vms_list = self.list_stack_ingress_vms(self.nova_client, stack_name)
                    ips_list = ips_ingress_list
                else:
                    vms_list = self.list_stack_egress_vms(self.nova_client, stack_name)
                    ips_list = ips_egress_list
                for i,vms in enumerate(vms_list):
                    az = getattr(vms, 'OS-EXT-AZ:availability_zone')
                    if az and vms.id not in fip_map.keys():
                        vms_map[az].append(vms)
                #print vms_map.items()

                # loop through ips list and assign to vms across azs evenly
                num_az = len(vms_map.keys())
                az_map = dict()
                for i,az in enumerate(vms_map):
                    az_map[i] = az
                print vms_map['az1']
                print vms_map['az2']
                print ips_list
                for i,ips in enumerate(ips_list):
                    max_az_len = -1
                    max_az = None
                    for j,az in enumerate(vms_map):
                        if len(vms_map[az]) > max_az_len and len(vms_map[az]) != 0:
                            max_az = az
                            max_az_len = len(vms_map[az])
                    if max_az is None:
                        print 'No more VM could associate floating IP'
                        exit(1)
                    vms = vms_map[max_az].pop()
                    fip = ips
                    #https://ask.openstack.org/en/question/88485/how-to-assign-a-floating-ip-using-openstack-python-sdk-and-nova-network/
                    instance = self.nova_client.servers.find(id=vms.id)
                    instance.add_floating_ip(fip)
                    if x == 0:
                        print 'ingress,'+fip+','+max_az+','+vms.name+','+vms.id
                    else:
                        print 'egress,'+fip+','+max_az+','+vms.name+','+vms.id

        # rlin starts to add more operations
        elif sys.argv[1] == 'substitute':
            stack_name = sys.argv[2]
            fip = sys.argv[3]

            # locate the original node
            original_node = None
            for ingress_node in self.list_stack_ingress_vms(self.nova_client, stack_name):
                fip_hit_count = [ True if fip else False in value for value in ingress_node.networks.values()]
                if sum(fip_hit_count) > 0:
                    print 'found ingress node', ingress_node.to_dict()["name"], 'with fip', fip
                    original_node = ingress_node
                    # print json.dumps(ingress_node.to_dict(), indent=4)
                    break
            original_node_in_dict = original_node.to_dict() if original_node else None

            # get a list of alternate nodes
            # - under same az
            # - with no fip assigned
            alternate_nodes = []

            if original_node_in_dict:
                for ingress_node in self.list_stack_ingress_vms(self.nova_client, stack_name):
                    ingress_node_in_dict = ingress_node.to_dict()
                    if original_node_in_dict["OS-EXT-AZ:availability_zone"] == ingress_node_in_dict["OS-EXT-AZ:availability_zone"]:
                        print 'a same az', original_node_in_dict["OS-EXT-AZ:availability_zone"], 'node found', original_node_in_dict["name"]
                        for addresses_value in ingress_node_in_dict["addresses"].values():
                            fip_value_count = [True if value["OS-EXT-IPS:type"] == "floating" else False for value in addresses_value]
                            if sum(fip_value_count) == 0:
                                alternate_nodes.append(ingress_node)
                                break

            print 'there are', len(alternate_nodes), 'node(s) found that fulfill "same az" and "no fip assigned"'
            for alternate_node in alternate_nodes:
                alternate_node_in_dict = alternate_node.to_dict()
                for addresses_value in alternate_node_in_dict["addresses"].values():
                    for value in addresses_value:
                        if value["OS-EXT-IPS:type"] == "fixed": print value["addr"]

        elif sys.argv[1] == 'deassociate':

            fip = sys.argv[2]

            self.deassociate_fip(fip, self.nova_client)

        elif sys.argv[1] == 'reassign':

            fip = sys.argv[2]
            new_node = sys.argv[3]

            self.deassociate_fip(fip, self.nova_client)
            self.reassign_fip(fip, new_node, self.nova_client)

        elif sys.argv[1] == 'list_ingest_floating':
            stack_name = sys.argv[2]
            if len(sys.argv) > 3:
                output_file = sys.argv[3]
            else:
                output_file = "list_ingest_floating.txt"

            ip_list = []
            with open(output_file, "w") as f:
                for ingress_node in self.list_stack_ingress_vms(self.nova_client, stack_name):
                    ingress_node_in_dict = ingress_node.to_dict()
                    for addresses_value in ingress_node_in_dict["addresses"].values():
                        ips = {"floating":"null", "fixed":"null"}
                        for value in addresses_value:
                            if value["OS-EXT-IPS:type"] == "floating":
                                ip_list.append(value["addr"])
                                ips["floating"] = value["addr"]
                            elif value["OS-EXT-IPS:type"] == "fixed":
                                ips["fixed"] = value["addr"]
                    f.write(ingress_node_in_dict["metadata"]["vos_roles"] + " "\
                     + ingress_node_in_dict["OS-EXT-AZ:availability_zone"]\
                      + " " + ips["fixed"] + " " + ips["floating"] + "\n")

            for ip in ip_list:
                print ip

        elif sys.argv[1] == 'list' or sys.argv[1] == 'list_json':
            if len(sys.argv) > 2:
                stack_name = sys.argv[2]
            else:
                stack_name = ""

            nodes = []
            # for stack_node in self.list_stack_vms(self.nova_client, stack_name):
            for stack_node in self.nova_client.servers.list():
                ips = {"floating":"null", "fixed":"null"}
                stack_node_in_dict = stack_node.to_dict()
                for addresses_value in stack_node_in_dict["addresses"].values():
                    ips = {"floating":"null", "fixed":"null"}
                    for value in addresses_value:
                        if value["OS-EXT-IPS:type"] == "floating":
                            ips["floating"] = value["addr"]
                        elif value["OS-EXT-IPS:type"] == "fixed":
                            ips["fixed"] = value["addr"]

                '''
                    power_states = [
                        'NOSTATE',      # 0x00
                        'Running',      # 0x01
                '''
                if stack_node_in_dict["OS-EXT-STS:power_state"] == 0:
                    power_state = "NOSTATE"
                elif stack_node_in_dict["OS-EXT-STS:power_state"] == 1:
                    power_state = "Running"
                else:
                    power_state = "unknown_power_state"

                node = dict()
                node["name"] = stack_node_in_dict["name"]
                node["status"] = stack_node_in_dict["status"]
                node["power_state"] = power_state
                node["availability_zone"] = stack_node_in_dict["OS-EXT-AZ:availability_zone"]
                node["fixed"] = ips["fixed"] if ips != None else "no_ips"
                node["floating"] = ips["floating"]
                node["vos_roles"] = stack_node_in_dict["metadata"]["vos_roles"] if u"vos_roles" in stack_node_in_dict["metadata"].keys() else "not_a_vos_node"
                nodes.append(node)

                if sys.argv[1] == 'list':
                    print stack_node_in_dict["OS-EXT-SRV-ATTR:host"] + " "\
                        + stack_node_in_dict["name"] + " "\
                        + stack_node_in_dict["status"] + " "\
                        + power_state + " "\
                        + stack_node_in_dict["OS-EXT-AZ:availability_zone"] + " "\
                        + ips["fixed"] + " " + ips["floating"] + " "\
                        + (stack_node_in_dict["metadata"]["vos_roles"] if u"vos_roles" in stack_node_in_dict["metadata"].keys() else "not_a_vos_node")


            if sys.argv[1] == 'list_json':
                # print json.dumps(nodes, indent=4)
                print nodes

        elif sys.argv[1] == 'reboot':
            if sys.argv[2] in ["soft", "hard"]:
                reboot_type = sys.argv[2]
            else:
                self._usage()
            private_ip = sys.argv[3]

            self.reboot_server(reboot_type, private_ip, self.nova_client)

        #print("Bye!")

if __name__ == '__main__':
    #if len(sys.argv) < 1 or sys.argv[1] == "-h" or sys.argv[1] == "--help":
    #    FIPHelper._usage()
    #    exit(1)
    try:
        helper = FIPHelper(sys.argv)
        helper.main(sys.argv)
    except RuntimeError:
        print('')
