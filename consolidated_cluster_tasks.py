#!/usr/bin/env python
######################################
# Script: consolidated_cluster_tasks.py
# Date: 07/23/2017
# Author: Satish Botla
# Version 1.1
######################################
import vos

mesos_master = "10.105.170.71"

mtasks = vos.mesos_get_tasks(mesos_master)

magents = vos.mesos_get_agents(mesos_master)
consolidated_list = []
for task in mtasks:
    for agent in magents:
        if(task['state'] == "TASK_RUNNING"):
            task_id = task['task_id']['value']
            task_name = task['name']
            framework_id = task['framework_id']['value']
            slave_id = task['agent_id']['value']
            task_state = task['state']
            memory = task['resources'][0]['scalar']['value']
            cpu = task['resources'][1]['scalar']['value']
            container_ip = task['statuses'][0]['container_status']['network_infos'][0]['ip_addresses'][0]['ip_address'] 
            docket_network = task['container']['docker']['network']
            hostname = agent['agent_info']['hostname']
            role = agent['agent_info']['attributes'][5]['text']['value']
            availabilty_zone = agent['agent_info']['attributes'][4]['text']['value']
            if(slave_id == agent['agent_info']['id']['value']):
                consolidated_list.append({'taskid':task_id,'taskname':task_name ,'frameworkid':framework_id,'slaveid': slave_id,'taskstate':task_state, 'memory':memory,'cpu':cpu,'role':role,'az':availabilty_zone,'hostname':hostname,'ip':container_ip,'docker_network':docket_network})
print "TASK_ID,TASKNAME,FRAMEWORK_ID,SLAVE_ID,TASK_STATE,CPU,MEMORY,ROLE,AVAILABILTY_ZONE,HOSTNAME,IP,DOCKER_NETWORK"

for x in consolidated_list:
    print "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" %(x['taskid'],x['taskname'],x['frameworkid'],x['slaveid'],x['taskstate'],x['memory'],x['cpu'],x['role'],x['az'],x['hostname'],x['ip'],x['docker_network'])

