#!/usr/bin/env python

from functools import wraps
from heatclient import client as heat_client
from heatclient.exc import HTTPInternalServerError
from kazoo.client import KazooClient
from kazoo.retry import KazooRetry
from keystoneauth1 import identity
from keystoneauth1 import session
from keystoneclient import session as kssession
from keystoneclient.auth.identity import v2 as v2_auth
from neutronclient.v2_0 import client as neutronclient
from novaclient import client as nova_client
from novaclient.exceptions import ClientException
from requests.auth import HTTPBasicAuth
from requests.exceptions import ConnectionError
from requests.exceptions import ReadTimeout
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import ConfigParser
import argparse
import base64
import json
import logging
import os
import re
import requests
import subprocess
import sys
import time
import yaml

# Global config

CONFIG_PROP_FILENAME = 'os-scale.prop'

DEFAULT_SLEEP_SECONDS = 10

VOS_SSH_USER = 'centos'

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Logging

logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger('os-scale')
# TODO Log level
logger.setLevel(logging.DEBUG)

# General helper functions

def retry(ExceptionToCheck, tries=4, delay=3, backoff=2, logger=logger):
  """Retry calling the decorated function using an exponential backoff.

  http://www.saltycrane.com/blog/2009/11/trying-out-retry-decorator-python/
  original from: http://wiki.python.org/moin/PythonDecoratorLibrary#Retry

  :param ExceptionToCheck: the exception to check. may be a tuple of exceptions to check
  :type ExceptionToCheck: Exception or tuple
  :param tries: number of times to try (not retry) before giving up
  :type tries: int
  :param delay: initial delay between retries in seconds
  :type delay: int
  :param backoff: backoff multiplier e.g. value of 2 will double the delay each retry
  :type backoff: int
  :param logger: logger to use. If None, print
  :type logger: logging.Logger instance
  """
  def deco_retry(f):
    @wraps(f)
    def f_retry(*args, **kwargs):
      mtries, mdelay = tries, delay
      while mtries > 1:
        try:
          return f(*args, **kwargs)
        except ExceptionToCheck, e:
          msg = '%s, retrying in %d seconds...' % (str(e), mdelay)
          if logger:
            logger.warning(msg)
          else:
            print msg
          time.sleep(mdelay)
          mtries -= 1
          mdelay *= backoff
      return f(*args, **kwargs)
    return f_retry  # true decorator
  return deco_retry

def query_yes_no(question, default='yes'):
  """Ask a yes/no question via raw_input() and return their answer.

  "question" is a string that is presented to the user.
  "default" is the presumed answer if the user just hits <Enter>.
  It must be "yes" (the default), "no" or None (meaning an answer is required of the user).

  The "answer" return value is True for "yes" or False for "no".

  http://stackoverflow.com/questions/3041986/apt-command-line-interface-like-yes-no-input
  """
  valid = {'yes': True, 'y': True, 'no': False, 'n': False}
  if default is None:
    prompt = ' [y/n] '
  elif default == 'yes':
    prompt = ' [Y/n] '
  elif default == 'no':
    prompt = ' [y/N] '
  else:
    raise ValueError('Invalid default yes/no answer: %s' % default)

  while True:
    sys.stdout.write(question + prompt)
    choice = raw_input().lower()
    if default is not None and choice == '':
      return valid[default]
    elif choice in valid:
      return valid[choice]
    else:
      sys.stdout.write('Please respond with "yes" or "no" (or "y" or "n").\n')

def execute_ssh_command(ip, port, user, key_file, command, sudo):
  if not port: port = 22
  ssh_command_array = []
  ssh_command_array.extend(['ssh', '-o', 'UserKnownHostsFile=/dev/null', '-o', 'StrictHostKeyChecking=no', '-i', key_file])
  if sudo == True:
    ssh_command_array.extend(['-tt'])
  ssh_command_array.extend(['-p', str(port), '{user}@{ip}'.format(user=user, ip=ip), command])
  ssh_process = subprocess.Popen(ssh_command_array, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  ssh_process.wait()
  ssh_return = {'exit_code': ssh_process.returncode, 'stdout_lines': ssh_process.stdout.readlines(), 'stderr_lines': ssh_process.stderr.readlines()}
  return ssh_return

LOCAL_SSH_TUNNEL_PORT = 2255

def execute_ssh_command_with_ssh_tunnel(tunnel_ip, tunnel_port, tunnel_user, tunnel_key_file, ssh_ip, ssh_port, ssh_user, ssh_key_file, ssh_command, ssh_sudo):
  if not tunnel_port: tunnel_port = 22
  if not ssh_port: ssh_port = 22
  tunnel_command_array = []
  tunnel_command_array.extend(['ssh', '-o', 'UserKnownHostsFile=/dev/null', '-o', 'StrictHostKeyChecking=no', '-i', tunnel_key_file])
  tunnel_command_array.extend(['-L', '{local_ssh_tunnel_port}:{ssh_ip}:{ssh_port}'.format(local_ssh_tunnel_port=LOCAL_SSH_TUNNEL_PORT, ssh_ip=ssh_ip, ssh_port=ssh_port), '-nNT'])
  tunnel_command_array.extend(['-p', str(tunnel_port), '{user}@{ip}'.format(user=tunnel_user, ip=tunnel_ip)])
  tunnel_process = subprocess.Popen(tunnel_command_array, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  time.sleep(DEFAULT_SLEEP_SECONDS)
  try:
    if tunnel_process and tunnel_process.poll() == None:
      return execute_ssh_command('127.0.0.1', LOCAL_SSH_TUNNEL_PORT, ssh_user, ssh_key_file, ssh_command, ssh_sudo)
    else:
      raise Exception('Failed to create SSH tunnel using command: {command}'.format(command=tunnel_command_array))
  finally:
    if tunnel_process and tunnel_process.poll() == None:
      tunnel_process.kill()

# https://www.ibm.com/developerworks/cloud/library/cl-openstack-pythonapis/

# Neutron functions
# https://github.com/openstack/python-neutronclient/blob/291b31e0e5eed01cbbe917a644e38c2cedafae3e/neutronclient/v2_0/client.py
# https://github.com/openstack/python-neutronclient/blob/291b31e0e5eed01cbbe917a644e38c2cedafae3e/neutronclient/neutron/v2_0/securitygroup.py
# http://docs.openstack.org/developer/python-neutronclient/usage/cli.html

def list_security_group_rules(
  neutron_c
  , security_group_id
  , direction
  , ether_type
  , ip_protocol
  , port_range_min
  , port_range_max
  , remote_ip_prefix
  , remote_security_group_id):
  params = {}
  if not security_group_id is None: params['security_group_id'] = security_group_id
  if not direction is None: params['direction'] = direction
  if not ether_type is None: params['ethertype'] = ether_type
  if not ip_protocol is None: params['protocol'] = ip_protocol
  if not port_range_min is None: params['port_range_min'] = port_range_min
  if not port_range_max is None: params['port_range_max'] = port_range_max
  if not remote_ip_prefix is None: params['remote_ip_prefix'] = remote_ip_prefix
  if not remote_security_group_id is None: params['remote_group_id'] = remote_security_group_id
  rules = neutron_c.list_security_group_rules(**params)['security_group_rules']
  # Mirantis OpenStack does not apply the 'filters' above and return all the rules...
  filtered_rules = []
  for rule in rules:
    rule_match = True
    if not security_group_id is None and rule['security_group_id'] != security_group_id: rule_match = False
    if not direction is None and rule['direction'] != direction: rule_match = False
    if not ether_type is None and rule['ethertype'] != ether_type: rule_match = False
    if not ip_protocol is None and rule['protocol'] != ip_protocol: rule_match = False
    if not port_range_min is None and rule['port_range_min'] != port_range_min: rule_match = False
    if not port_range_max is None and rule['port_range_max'] != port_range_max: rule_match = False
    if not remote_ip_prefix is None and rule['remote_ip_prefix'] != remote_ip_prefix: rule_match = False
    if not remote_security_group_id is None and rule['remote_group_id'] != remote_security_group_id: rule_match = False
    if rule_match:
      filtered_rules.append(rule)
  return filtered_rules

def delete_security_group_rule(
  neutron_c
  , security_group_id
  , direction
  , ether_type
  , ip_protocol
  , port_range_min
  , port_range_max
  , remote_ip_prefix
  , remote_security_group_id):
  rules = list_security_group_rules(
    neutron_c=neutron_c
    , security_group_id=security_group_id
    , direction=direction
    , ether_type=ether_type
    , ip_protocol=ip_protocol
    , port_range_min=port_range_min
    , port_range_max=port_range_max
    , remote_ip_prefix=remote_ip_prefix
    , remote_security_group_id=remote_security_group_id
  )
  if len(rules) > 0:
    if len(rules) == 1:
      neutron_c.delete_security_group_rule(rules[0]['id'])
    else:
      raise Exception('Deleting multiple security group rules is NOT supported')

def create_security_group_rule(
  neutron_c
  , security_group_id
  , direction
  , ether_type
  , ip_protocol
  , port_range_min
  , port_range_max
  , remote_ip_prefix
  , remote_security_group_id
  , retry=3):
  rules = list_security_group_rules(
    neutron_c=neutron_c
    , security_group_id=security_group_id
    , direction=direction
    , ether_type=ether_type
    , ip_protocol=ip_protocol
    , port_range_min=port_range_min
    , port_range_max=port_range_max
    , remote_ip_prefix=remote_ip_prefix
    , remote_security_group_id=remote_security_group_id
  )
  if len(rules) == 0:
    body = {
      'security_group_rule': {
        'security_group_id': security_group_id,
        'direction': direction,
        'ethertype': ether_type,
        'protocol': ip_protocol,
        'port_range_min': port_range_min,
        'port_range_max': port_range_max,
        'remote_ip_prefix': remote_ip_prefix,
        'remote_group_id': remote_security_group_id
      }
    }
    rule = neutron_c.create_security_group_rule(body)
    # Check rule is created ...
    rules = list_security_group_rules(
      neutron_c=neutron_c
      , security_group_id=security_group_id
      , direction=direction
      , ether_type=ether_type
      , ip_protocol=ip_protocol
      , port_range_min=port_range_min
      , port_range_max=port_range_max
      , remote_ip_prefix=remote_ip_prefix
      , remote_security_group_id=remote_security_group_id
    )
    if len(rules) == 0:
      if retry > 0:
        return create_security_group_rule(
          neutron_c=neutron_c
          , security_group_id=security_group_id
          , direction=direction
          , ether_type=ether_type
          , ip_protocol=ip_protocol
          , port_range_min=port_range_min
          , port_range_max=port_range_max
          , remote_ip_prefix=remote_ip_prefix
          , remote_security_group_id=remote_security_group_id
          , retry=retry-1
        )
      else:
        raise Exception('Failed to create security group rule')
    elif len(rules) == 1:
      return rule['security_group_rule']
    else:
      raise Exception('Unexpected result in create_security_group_rule')
  elif len(rules) == 1:
    return rules[0]
  else:
    raise Exception('Invalid inputs passed into create_security_group_rule')

# Nova functions

OS_SERVER_STATUS_ACTIVE = 'ACTIVE'
OS_SERVER_STATUS_SHUTOFF = 'SHUTOFF'

@retry(ClientException)
def shut_off_server(nova_c, server_id, wait_for_shut_off=True):
  nova_c.servers.stop(server_id)
  if wait_for_shut_off:
    while True:
      server = get_server_by_id(nova_c, server_id)
      server_status = server['status']
      logger.debug('Server "{server_id}" status: {server_status}'.format(server_id=server_id, server_status=server_status))
      if server_status == OS_SERVER_STATUS_SHUTOFF:
        break
      time.sleep(DEFAULT_SLEEP_SECONDS)

@retry(ClientException)
def terminate_server(nova_c, server_id, wait_for_terminate=True):
  nova_c.servers.delete(server_id)
  if wait_for_terminate:
    while True:
      server = get_server_by_id(nova_c, server_id)
      if server:
        logger.debug('Server "{server_id}" status: {server_status}'.format(server_id=server_id, server_status=server['status']))
      else:
        break
      time.sleep(DEFAULT_SLEEP_SECONDS)

def remove_floating_ip(nova_c, server_id, floating_ip_ip):
  server = nova_c.servers.find(id=server_id)
  floating_ip_id = get_floating_ip_by_ip(nova_c, floating_ip_ip)['id']
  floating_ip = nova_c.floating_ips.get(floating_ip_id)
  server.remove_floating_ip(floating_ip)

def add_floating_ip(nova_c, server_id, floating_ip_ip):
  server = nova_c.servers.find(id=server_id)
  floating_ip_id = get_floating_ip_by_ip(nova_c, floating_ip_ip)['id']
  floating_ip = nova_c.floating_ips.get(floating_ip_id)
  server.add_floating_ip(floating_ip)

def get_floating_ip_by_ip(nova_c, floating_ip_ip):
  floating_ips_key_ip = get_floating_ips(nova_c)[1]
  if floating_ip_ip in floating_ips_key_ip:
    return floating_ips_key_ip[floating_ip_ip]
  return None

def get_floating_ip_by_id(nova_c, floating_ip_id):
  floating_ips_key_id = get_floating_ips(nova_c)[0]
  if floating_ip_id in floating_ips_key_id:
    return floating_ips_key_id[floating_ip_id]
  return None

def get_floating_ips(nova_c):
  floating_ips_key_id = {}
  floating_ips_key_ip = {}
  floating_ips_list = nova_c.floating_ips.list()
  for fip in floating_ips_list:
    f = fip.to_dict()
    floating_ip_id = f['id']
    floating_ip_ip = f['ip']
    floating_ip_associated_instance_id = f['instance_id']
    floating_ip_associated_fixed_ip = f['fixed_ip']
    floating_ip = {}
    floating_ip['id'] = floating_ip_id
    floating_ip['ip'] = floating_ip_ip
    floating_ip['associated_instance_id'] = floating_ip_associated_instance_id
    floating_ip['associated_fixed_ip'] = floating_ip_associated_fixed_ip
    floating_ips_key_id[floating_ip_id] = floating_ip
    floating_ips_key_ip[floating_ip_ip] = floating_ip
  return floating_ips_key_id, floating_ips_key_ip

def get_image_by_name(nova_c, image_name):
  images_key_name = get_images(nova_c)[1]
  if image_name in images_key_name:
    return images_key_name[image_name]
  return None

def get_image_by_id(nova_c, image_id):
  images_key_id = get_images(nova_c)[0]
  if image_id in images_key_id:
    return images_key_id[image_id]
  return None

def get_images(nova_c):
  images_key_id = {}
  images_key_name = {}
  images_list = nova_c.images.list()
  for img in images_list:
    i = img.to_dict()
    image_id = i['id']
    image_name = i['name']
    image_status = i['status']
    image = {}
    image['id'] = image_id
    image['name'] = image_name
    image['status'] = image_status
    images_key_id[image_id] = image
    images_key_name[image_name] = image
  return images_key_id, images_key_name

# TODO Performance of get_server*, get_image*, etc.
def get_server_by_name(nova_c, server_name):
  servers_key_name = get_servers(nova_c)[1]
  if server_name in servers_key_name:
    return servers_key_name[server_name]
  return None

def get_server_by_id(nova_c, server_id):
  servers_key_id = get_servers(nova_c)[0]
  if server_id in servers_key_id:
    return servers_key_id[server_id]
  return None

@retry(ClientException)
def get_servers(nova_c, stack_id=None):
  servers_key_id = {}
  servers_key_name = {}
  servers_list = nova_c.servers.list()
  for ser in servers_list:
    s = ser.to_dict()

    server_id = s['id']
    server_name = s['name']
    server_status = s['status']
    server_image_id = s['image']['id']
    server_availability_zone = s['OS-EXT-AZ:availability_zone']
    server_public_ips = []
    server_private_ips = []
    addresses_0 = s['addresses'].itervalues().next()
    for a in addresses_0:
      if a['OS-EXT-IPS:type'] == 'floating':
        server_public_ips.append(a['addr'])
      if a['OS-EXT-IPS:type'] == 'fixed':
        server_private_ips.append(a['addr'])
    server_vos_roles = []
    if s['metadata'].has_key('vos_roles'):
      server_vos_roles = s['metadata']['vos_roles'].split(',')
    server_stack_id = ''
    if s['metadata'].has_key('stack_id'):
      server_stack_id = s['metadata']['stack_id']

    server = {}
    server['id'] = server_id
    server['name'] = server_name
    server['status'] = server_status
    server['image_id'] = server_image_id
    server['availability_zone'] = server_availability_zone
    server['public_ips'] = server_public_ips
    server['private_ips'] = server_private_ips
    server['vos_roles'] = server_vos_roles
    server['stack_id'] = server_stack_id

    if stack_id is None or stack_id == server_stack_id:
      servers_key_id[server_id] = server
      servers_key_name[server_name] = server

  return servers_key_id, servers_key_name

# Heat functions

OS_STACK_STATUS_CREATE_COMPLETE = 'CREATE_COMPLETE'
OS_STACK_STATUS_CREATE_FAILED = 'CREATE_FAILED'
OS_STACK_STATUS_UPDATE_COMPLETE = 'UPDATE_COMPLETE'
OS_STACK_STATUS_UPDATE_FAILED = 'UPDATE_FAILED'

def get_stack_template(heat_c, stack_id):
  template = heat_c.stacks.template(stack_id)
  return template

def get_stack_security_group_id(heat_c, stack_id):
  resources = heat_c.resources.list(stack_id=stack_id)
  for resource in resources:
    if resource.to_dict()['resource_type'] == 'OS::Neutron::SecurityGroup':
      return resource.to_dict()['physical_resource_id']

@retry(HTTPInternalServerError)
def delete_stack(heat_c, stack_id, wait_for_completion=True):
  heat_c.stacks.delete(stack_id)
  if wait_for_completion:
    while True:
      stack = get_stack_by_id(heat_c, stack_id)
      if stack:
        logger.debug('Stack "{stack_name}" status: {stack_status}'.format(stack_name=stack['name'], stack_status=stack['status']))
      else:
        break
      time.sleep(DEFAULT_SLEEP_SECONDS)

@retry(HTTPInternalServerError)
def update_stack(heat_c, stack_id, template, parameters, wait_for_completion=True):
  template_content = ''
  with open(template) as template_file:
    template_content = template_file.read()
  fields = {
    'stack_id': stack_id,
    'template': template_content,
    'parameters': parameters,
    'existing': True,
    'disable_rollback': True,
    'timeout_mins': 60
  }
  heat_c.stacks.update(**fields)
  stack = get_stack_by_id(heat_c, stack_id)
  if wait_for_completion:
    while True:
      stack = get_stack_by_id(heat_c, stack_id)
      stack_status = stack['status']
      logger.debug('Stack "{stack_name}" status: {stack_status}'.format(stack_name=stack['name'], stack_status=stack_status))
      if stack_status == OS_STACK_STATUS_UPDATE_COMPLETE or stack_status == OS_STACK_STATUS_UPDATE_FAILED:
        break
      time.sleep(DEFAULT_SLEEP_SECONDS)
  return stack

@retry(HTTPInternalServerError)
def create_stack(heat_c, stack_name, template, parameters, wait_for_completion=True):
  template_content = ''
  with open(template) as template_file:
    template_content = template_file.read()
  fields = {
    'stack_name': stack_name,
    'template': template_content,
    'parameters': parameters,
    'existing': False,
    'disable_rollback': True,
    'timeout_mins': 60
  }
  heat_c.stacks.create(**fields)
  stack = get_stack_by_name(heat_c, stack_name)
  if wait_for_completion:
    while True:
      stack = get_stack_by_name(heat_c, stack_name)
      stack_status = stack['status']
      logger.debug('Stack "{stack_name}" status: {stack_status}'.format(stack_name=stack['name'], stack_status=stack_status))
      if stack_status == OS_STACK_STATUS_CREATE_COMPLETE or stack_status == OS_STACK_STATUS_CREATE_FAILED:
        break
      time.sleep(DEFAULT_SLEEP_SECONDS)
  return stack

def get_stack_details(heat_c, stack_id):
  s_dict = heat_c.stacks.get(stack_id).to_dict()
  s_id = s_dict['id']
  s_name = s_dict['stack_name']
  s_status = s_dict['stack_status']
  s_parameters = s_dict['parameters']
  stack = {}
  stack['id'] = s_id
  stack['name'] = s_name
  stack['status'] = s_status
  stack['parameters'] = s_parameters
  return stack

def get_stack_by_name(heat_c, stack_name):
  stacks_key_name = get_stacks(heat_c)[1]
  if stack_name in stacks_key_name:
    return stacks_key_name[stack_name]
  return None

def get_stack_by_id(heat_c, stack_id):
  stacks_key_id = get_stacks(heat_c)[0]
  if stack_id in stacks_key_id:
    return stacks_key_id[stack_id]
  return None

def get_stacks(heat_c):
  stacks_key_id = {}
  stacks_key_name = {}
  stacks_list = heat_c.stacks.list()
  for s in stacks_list:
    s_dict = s.to_dict()
    s_id = s_dict['id']
    s_name = s_dict['stack_name']
    s_status = s_dict['stack_status']
    stack = {}
    stack['id'] = s_id
    stack['name'] = s_name
    stack['status'] = s_status
    stacks_key_id[s_id] = stack
    stacks_key_name[s_name] = stack
  return stacks_key_id, stacks_key_name

# OpenStack client functions

def get_heat_client(os_auth_url, os_username, os_password, os_project):
  keystone_auth = v2_auth.Password(os_auth_url, username=os_username, password=os_password, tenant_name=os_project)
  keystone_session = kssession.Session(verify=False, cert=None, timeout=None)
  heat_endpoint = keystone_auth.get_endpoint(keystone_session, service_type='orchestration', interface='publicURL')
  kwargs = {
    'auth_url': os_auth_url,
    'username': os_username,
    'password': os_password,
    'auth': keystone_auth,
    'session': keystone_session,
    'service_type': 'orchestration',
    'endpoint_type': 'publicURL'
  }
  heat = heat_client.Client('1', heat_endpoint, **kwargs)
  return heat

def get_nova_client(os_auth_url, os_username, os_password, os_project):
  nova = nova_client.Client('2', os_username, os_password, os_project, os_auth_url)
  return nova

def get_neutron_client(os_auth_url, os_username, os_password, os_project):
  kwargs = {
    'auth_url': os_auth_url,
    'username': os_username,
    'password' : os_password,
    'project_name': os_project
 }
  auth = identity.Password(**kwargs)
  sess = session.Session(auth=auth)
  neutron = neutronclient.Client(session=sess)
  return neutron

#

def sanitize_stack_parameters(
  template, image=None, flavor=None
  , ingest_nodes_num=None, egress_nodes_num=None, control_nodes_num=None
  , private_network_name=None, private_network_range=None, ntp_servers=None
  , bintray_username=None, bintray_password=None
  , mediagrid_mount_point=None, mediagrid_username=None, mediagrid_password=None):
  parameters = {
    'image': image,
    'flavor': flavor,
    'node_num': ingest_nodes_num,
    'egress_node_num': egress_nodes_num,
    'control_node_num': control_nodes_num,
    'private_net_name': private_network_name,
    'private_net_range': private_network_range,
    'ntp_servers': ntp_servers,
    'bintray_username': bintray_username,
    'bintray_password': bintray_password,
    'mediagrid_mountpoint': mediagrid_mount_point,
    'mediagrid_username': mediagrid_username,
    'mediagrid_password': mediagrid_password
  }

  sanitized_parameters = {}
  with open(template, 'r') as t:
    doc = yaml.load(t)
    for parameter in doc['parameters']:
      if parameters.has_key(parameter):
        sanitized_parameters[parameter] = parameters[parameter]

  return sanitized_parameters

def make_stack_scale_template(stack_template, stack_initial_ingest_nodes_num, stack_initial_egress_nodes_num, stack_initial_control_nodes_num):
  stack_scale_template = '{stack_template}-scale'.format(stack_template=stack_template)
  template = {}
  with open(stack_template, 'r') as f:
    template = yaml.load(f)
  # In NGDE-1557:
  # ['wait_condition']['properties']['count'] is hard coded to 1
  # 'egress_wait_condition' and 'control_wait_condition' are removed
  # '$node_num' and '$ingest_node_num' and '$egress_node_num' are removed
  template['resources']['wait_condition']['properties']['count'] = stack_initial_ingest_nodes_num
  if 'egress_wait_condition' in template['resources']:
    template['resources']['egress_wait_condition']['properties']['count'] = stack_initial_egress_nodes_num
  if 'control_wait_condition' in template['resources']:
    template['resources']['control_wait_condition']['properties']['count'] = stack_initial_control_nodes_num
  if '$node_num' in template['resources']['vos_node_init_script_common']['properties']['config']['str_replace']['params']:
    template['resources']['vos_node_init_script_common']['properties']['config']['str_replace']['params']['$node_num'] = stack_initial_control_nodes_num
  if '$ingest_node_num' in template['resources']['vos_node_init_script_common']['properties']['config']['str_replace']['params']:
    template['resources']['vos_node_init_script_common']['properties']['config']['str_replace']['params']['$ingest_node_num'] = stack_initial_ingest_nodes_num
  if '$egress_node_num' in template['resources']['vos_node_init_script_common']['properties']['config']['str_replace']['params']:
    template['resources']['vos_node_init_script_common']['properties']['config']['str_replace']['params']['$egress_node_num'] = stack_initial_egress_nodes_num
  with open(stack_scale_template, 'w') as f:
    f.write(yaml.dump(template, default_flow_style=False))
  return stack_scale_template

# Main helper functions (config)

class PropertiesParser(object):
  SECTION_HEADER = 'Default'

  def __init__(self, config_path):
    self.parser = ConfigParser.RawConfigParser()
    self.section_read = False
    self.parser_initialized = False
    self.config_file = open(config_path)

  def readline(self):
    if not self.section_read:
      try:
        return '[' + self.SECTION_HEADER + ']\n'
      finally:
        self.section_read = True
    else:
      return self.config_file.readline()

  def init_parser(self):
    if not self.parser_initialized:
      self.parser.readfp(self)
      self.parser_initialized = True

  def get(self, option):
    self.init_parser()
    return self.parser.get(self.SECTION_HEADER, option)

  def has_option(self, option):
    self.init_parser()
    return self.parser.has_option(self.SECTION_HEADER, option)

def get_config_value(name, envname, config):
  if config:
    if config.has_option(name):
      value = config.get(name)
      return value
    value = os.environ.get(envname)
    if value:
      return value
  return None

def get_arguments_parser(config):
  parser = argparse.ArgumentParser(description='os-scale')

  parser.add_argument('-y', '--yes', action='store_true')

  parser.add_argument('--config',
    default=CONFIG_PROP_FILENAME,
    help='Configuration properties filename')

  parser.add_argument('--os-username',
    default=get_config_value('os.username', 'OS_USERNAME', config),
    help='OpenStack username')
  parser.add_argument('--os-password',
    default=get_config_value('os.password', 'OS_PASSWORD', config),
    help='OpenStack password')
  parser.add_argument('--os-project',
    default=get_config_value('os.project', 'OS_PROJECT', config),
    help='OpenStack project')
  parser.add_argument('--os-auth-url',
    default=get_config_value('os.auth.url', 'OS_AUTH_URL', config),
    help='OpenStack auth URL, e.g. http://172.19.121.11:5000/v2.0/')

  parser.add_argument('--stack-name',
    default=get_config_value('stack.name', 'STACK_NAME', config),
    help='Stack name')
  #parser.add_argument('--stack-template',
  #  default=get_config_value('stack.template', 'STACK_TEMPLATE', config),
  #  help='Stack template')

  #parser.add_argument('--stack-image',
  #  default=get_config_value('stack.image', 'STACK_IMAGE', config),
  #  help='Stack image')
  #parser.add_argument('--stack-flavor',
  #  default=get_config_value('stack.flavor', 'STACK_FLAVOR', config),
  #  help='Stack flavor')
  parser.add_argument('--stack-ingest-nodes-num',
    default=get_config_value('stack.ingest.nodes.num', 'STACK_INGEST_NODES_NUM', config),
    help='Stack ingest nodes num')
  parser.add_argument('--stack-egress-nodes-num',
    default=get_config_value('stack.egress.nodes.num', 'STACK_EGRESS_NODES_NUM', config),
    help='Stack egress nodes num')
  parser.add_argument('--stack-control-nodes-num',
    default=get_config_value('stack.control.nodes.num', 'STACK_CONTROL_NODES_NUM', config),
    help='Stack control nodes num')
  parser.add_argument('--stack-initial-ingest-nodes-num',
    default=get_config_value('stack.initial.ingest.nodes.num', 'STACK_INITIAL_INGEST_NODES_NUM', config),
    help='Stack initial ingest nodes num')
  parser.add_argument('--stack-initial-egress-nodes-num',
    default=get_config_value('stack.initial.egress.nodes.num', 'STACK_INITIAL_EGRESS_NODES_NUM', config),
    help='Stack initial egress nodes num')
  parser.add_argument('--stack-initial-control-nodes-num',
    default=get_config_value('stack.initial.control.nodes.num', 'STACK_INITIAL_CONTROL_NODES_NUM', config),
    help='Stack initial control nodes num')

  #parser.add_argument('--stack-private-network-name',
  #  default=get_config_value('stack.private.network.name', 'STACK_PRIVATE_NETWORK_NAME', config),
  #  help='Stack private network name')
  #parser.add_argument('--stack-private-network-range',
  #  default=get_config_value('stack.private.network.range', 'STACK_PRIVATE_NETWORK_RANGE', config),
  #  help='Stack private network range')
  #parser.add_argument('--stack-ntp-servers',
  #  default=get_config_value('stack.ntp.servers', 'STACK_NTP_SERVERS', config),
  #  help='Stack NTP servers')

  #parser.add_argument('--stack-bintray-username',
  #  default=get_config_value('stack.bintray.username', 'STACK_BINTRAY_USERNAME', config),
  #  help='Stack Bintray username')
  parser.add_argument('--stack-bintray-password',
    default=get_config_value('stack.bintray.password', 'STACK_BINTRAY_PASSWORD', config),
    help='Stack Bintray password')

  #parser.add_argument('--stack-mediagrid-mount-point',
  #  default=get_config_value('stack.mediagrid.mount.point', 'STACK_MEDIAGRID_MOUNT_POINT', config),
  #  help='Stack MediaGrid mount point')
  #parser.add_argument('--stack-mediagrid-username',
  #  default=get_config_value('stack.mediagrid.username', 'STACK_MEDIAGRID_USERNAME', config),
  #  help='Stack MediaGrid username')
  parser.add_argument('--stack-mediagrid-password',
    default=get_config_value('stack.mediagrid.password', 'STACK_MEDIAGRID_PASSWORD', config),
    help='Stack MediaGrid password')

  return parser

# Main

if __name__ == '__main__':
  # http://stackoverflow.com/questions/107705/disable-output-buffering
  # reopen stdout file descriptor with write mode
  # and 0 as the buffer size (unbuffered)
  sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

  # Get confirmation
  logger.warning('###################################################################################################')
  logger.warning('############################################# WARNING #############################################')
  logger.warning('###################################################################################################')
  logger.warning('PLEASE DO NOT USE IT IF YOU ARE NOT SURE WHAT YOU ARE DOING AS IT CAN DESTROY A CLUSTER COMPLETELY')
  logger.warning('###################################################################################################')
  if not '--yes' in sys.argv and not query_yes_no(question='Do you know what you are doing?', default='no'):
    sys.exit(1)

  # Parse arguments
  config = None
  if os.path.isfile(CONFIG_PROP_FILENAME):
    config = PropertiesParser(CONFIG_PROP_FILENAME)
  parser = get_arguments_parser(config)
  args = parser.parse_args()
  if args.config != CONFIG_PROP_FILENAME:
    config = PropertiesParser(args.config)
    parser = get_argument_parser(config)
    args = parser.parse_args()
    CONFIG_PROP_FILENAME = args.config

  os_username = args.os_username
  os_password = args.os_password
  os_project = args.os_project
  os_auth_url = args.os_auth_url

  stack_name = args.stack_name
  #stack_template = args.stack_template

  #stack_image = args.stack_image
  #stack_flavor = args.stack_flavor
  stack_ingest_nodes_num = int(args.stack_ingest_nodes_num)
  stack_egress_nodes_num = int(args.stack_egress_nodes_num)
  stack_control_nodes_num = int(args.stack_control_nodes_num)
  stack_initial_ingest_nodes_num = int(args.stack_initial_ingest_nodes_num)
  stack_initial_egress_nodes_num = int(args.stack_initial_egress_nodes_num)
  stack_initial_control_nodes_num = int(args.stack_initial_control_nodes_num)

  #stack_private_network_name = args.stack_private_network_name
  #stack_private_network_range = args.stack_private_network_range
  #stack_ntp_servers = args.stack_ntp_servers

  #stack_bintray_username = args.stack_bintray_username
  stack_bintray_password = args.stack_bintray_password

  #stack_mediagrid_mount_point = args.stack_mediagrid_mount_point
  #stack_mediagrid_username = args.stack_mediagrid_username
  stack_mediagrid_password = args.stack_mediagrid_password
  
  # Init OpenStack clients
  heat_c = get_heat_client(os_auth_url, os_username, os_password, os_project)
  #nova_c = get_nova_client(os_auth_url, os_username, os_password, os_project)
  #neutron_c = get_neutron_client(os_auth_url, os_username, os_password, os_project)

  # Make stack scale template
  stack_template_object = get_stack_template(heat_c, stack_name)
  stack_template = 'os-scale-template.yaml'
  with open(stack_template, 'w') as f:
    f.write(yaml.safe_dump(stack_template_object, default_flow_style=False))
  stack_scale_template = make_stack_scale_template(stack_template, stack_initial_ingest_nodes_num, stack_initial_egress_nodes_num, stack_initial_control_nodes_num)

  # Get parameters from current stack
  stack_details = get_stack_details(heat_c, stack_name)
  stack_image = stack_details['parameters']['image']
  stack_flavor = stack_details['parameters']['flavor']
  stack_private_network_name = stack_details['parameters']['private_net_name']
  stack_private_network_range = stack_details['parameters']['private_net_range']
  stack_ntp_servers = stack_details['parameters']['ntp_servers']
  stack_bintray_username = stack_details['parameters']['bintray_username']
  stack_mediagrid_mount_point = stack_details['parameters']['mediagrid_mountpoint']
  stack_mediagrid_username = stack_details['parameters']['mediagrid_username']

  # Update/Scale stack
  stack_update_parameters = sanitize_stack_parameters(
    template=stack_scale_template
    , image=stack_image
    , flavor=stack_flavor
    , ingest_nodes_num=int(stack_ingest_nodes_num)
    , egress_nodes_num=int(stack_egress_nodes_num)
    , control_nodes_num=int(stack_control_nodes_num)
    , private_network_name=stack_private_network_name
    , private_network_range=stack_private_network_range
    , ntp_servers=eval(stack_ntp_servers)
    , bintray_username=stack_bintray_username
    , bintray_password=stack_bintray_password
    , mediagrid_mount_point=stack_mediagrid_mount_point
    , mediagrid_username=stack_mediagrid_username
    , mediagrid_password=stack_mediagrid_password
  )
  new_stack = update_stack(heat_c, stack_name, stack_scale_template, stack_update_parameters, False)