#!/bin/bash

# Sanity check
if [[ $# -lt 1 ]]; then
    echo "Usage: $0 [NFS_MOUNTPOINT]"
    echo "where"
    echo "   NFS_MOUNTPOINT - NFS Server and mount path (e.g. 1.2.3.4:/ifs/folder)"
    exit
elif [[ "$(whoami)" != "root" ]]; then
    echo "This script needs to be run under root account. Change to root as follow:"
    echo "   sudo su -"
    exit
fi
UVP_COOKBOOKS_URL="https://harmonicinc.bintray.com/repo/UVP_Cookbooks/1.1.0.0-eng.1816/UVP_Cookbooks_output.tgz"
NFS_MOUNTPOINT=$1

echo "Enabling NFS mounting on OpenStack DE ..."
echo "   NFS Mount point: ${NFS_MOUNTPOINT}"

echo " > Stop ObjectiveFS"
systemctl stop mount_objectivefs
systemctl disable mount_objectivefs

echo " > Download UVP_Cookbooks: ${UVP_COOKBOOKS_URL}"
wget --user=$(cat /opt/harmonic/node.json | jq -r .vos_middlewares.bintray_auth.user_name) --password=$(cat /opt/harmonic/node.json | jq -r .vos_middlewares.bintray_auth.api_key) ${UVP_COOKBOOKS_URL}
if [[ ! -s UVP_Cookbooks_output.tgz ]]; then
    echo "Download cookbooks from Bintray FAILED"
    exit 1
fi

echo " > Install NFS Recipe"
tar zxvf UVP_Cookbooks_output.tgz > /dev/null
cp -f UVP_Cookbooks/vos_middlewares/recipes/install_nfs.rb /opt/harmonic/UVP_Cookbooks/vos_middlewares/recipes
cp -f UVP_Cookbooks/vos_middlewares/attributes/nfs.rb /opt/harmonic/UVP_Cookbooks/vos_middlewares/attributes
cp -f UVP_Cookbooks/vos_middlewares/files/default/bin/mount_nfs /opt/harmonic/UVP_Cookbooks/vos_middlewares/files/default/bin
cp -f UVP_Cookbooks/vos_middlewares/files/centos/init_scripts/mount_nfs.service /opt/harmonic/UVP_Cookbooks/vos_middlewares/files/centos/init_scripts
rm -rf UVP_Cookbooks UVP_Cookbooks_output.tgz
chef-solo -o vos_middlewares::install_nfs

echo " > Configure mount_nfs service"
mkdir -p /etc/systemd/system/mount_nfs.service.d
cat > /etc/systemd/system/mount_nfs.service.d/environ.conf << EOH
[Service]
Environment="NFS_DEPLOY_ENV=openstack"
Environment="NFS_DEVICE=${NFS_MOUNTPOINT}"
EOH

echo " > Restart mount_nfs service"
systemctl stop mount_nfs
umount -l /mnt/nfsv4
systemctl daemon-reload
systemctl enable mount_nfs
systemctl start mount_nfs

sleep 10
echo " > Check service status"
systemctl status mount_nfs
echo " > Check mount status"
mount -l | grep nfsv4 || echo "NFS mount on ${NFS_MOUNTPOINT} FAILED"

echo "Done!"
