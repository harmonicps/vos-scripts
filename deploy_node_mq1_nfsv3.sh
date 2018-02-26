#!/bin/bash
#sudo cp -f 87-tcp_tuning.conf /etc/sysctl.d
#sudo chkconfig tune_default_route on
#sudo service tune_default_route start
#sysctl --system
# sudo docker load -i sspea_1000_30.tgz
sudo cp -f node.json /opt/harmonic
echo "Start Heat VOS deployment @ $(date +'%Y-%m-%dT%H:%M:%S%z') for node: `hostname -s` ..." > /var/log/heat_vos_setup.log
echo `hostname` > /etc/hostname
echo preserve_hostname: true >> /etc/cloud/cloud.cfg
sleep 2
systemctl enable nodes_discover_me.service
if [ $? -ne 0 ] ; then exit_deploy 1 "ENABLE NODES DISCOVERY FAILED" ; fi
systemctl restart nodes_discover_me.service
if [ $? -ne 0 ] ; then exit_deploy 1 "START NODES DISCOVERY FAILED" ; fi
service collectd restart
if [ $? -ne 0 ] ; then exit_deploy 1 "COLLECTD RESTART FAILED" ; fi
package-cleanup --oldkernels --count=1 -y
if [ $? -ne 0 ] ; then exit_deploy 1 "PACKAGE CLEANUP FAILED" ; fi
#Requests Network configuration from Nova as the incorrect NameServer comes up.
dhclient eth0
sed -i.bak -e 's/^Defaults\s\+requiretty/# \0/' /etc/sudoers
# Set MQ to 1 queue Only
sudo sed -i.bak 's/pre_set_value=4/pre_set_value=1/g' /sbin/ifup-local
sudo ethtool -L eth0 combined 1
sudo sed -i.bak 's/"-L eth0 combined 4"/"-L eth0 combined 1"/g' /etc/sysconfig/network-scripts/ifcfg-eth0
#Sets NFS to Version 3 as requested by AT&T
sudo sed -i.bak "s/mount_info\['options'\] = '-o nfsvers=4,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,async'/mount_info\['options'\] = '-o nfsvers=3,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,async,nolock,noatime,nodiratime,tcp'/g" /usr/local/bin/mount_nfs 
sudo sed -i.bak "s/command = 'timeout 60 mount -t nfs4 {options} {device} {mount_path}'.format(options=options, device=device, mount_path=mount_path)/command = 'timeout 60 mount -t nfs {options} {device} {mount_path}'.format(options=options, device=device, mount_path=mount_path)/g" /usr/local/bin/mount_nfs
/opt/chef/bin/chef-solo -o vos_middlewares::enable_docker_proxy,vos_middlewares::configuration | tee -a /var/log/heat_vos_setup.log
echo "Waiting for register middleware images ..."
sleep 120
python /usr/local/bin/register_middleware_images.py
SETUP_STATUS=${PIPESTATUS[0]}
cp -f /etc/sudoers.bak /etc/sudoers
if [ $SETUP_STATUS -eq 0 ] ; then echo "SETUP COMPLETED" ; else echo "SETUP FAILED" ; fi

