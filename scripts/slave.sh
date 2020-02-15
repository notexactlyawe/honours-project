#!/bin/bash
#set -u
#set -x
# deploy sgx on emulab
SCRIPTDIR=$(dirname "$0")
WORKINGDIR='/local/repository'
username=$(id -u)
usergid=$(id -g)

sudo chown ${username}:${usergid} ${WORKINGDIR}/ -R
cd $WORKINGDIR
exec >> ${WORKINGDIR}/deploy.log
exec 2>&1

KUBEHOME="${WORKINGDIR}/kube/"
mkdir -p $KUBEHOME && cd $KUBEHOME
export KUBECONFIG=$KUBEHOME/admin.conf

curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add
echo "deb http://apt.kubernetes.io/ kubernetes-bionic main" | sudo tee -a /etc/apt/sources.list.d/kubernetes.list

cd $WORKINGDIR
#git clone git@gitlab.flux.utah.edu:licai/deepstitch.git

sudo apt-get update
sudo apt-get -y install build-essential libffi-dev python python-dev  \
python-pip automake autoconf libtool indent vim tmux jq

# learn from this: https://blog.csdn.net/yan234280533/article/details/75136630
sudo apt-get -y install  docker-ce kubelet kubeadm kubectl kubernetes-cni golang-go jq
sudo docker version
sudo swapoff -a

master_token=''
while [ -z $master_token ] 
do
    master_token=`ssh -o StrictHostKeyChecking=no m "export KUBECONFIG='/local/repository/kube/admin.conf' &&   kubeadm token list |grep authentication | cut -d' ' -f 1"`;
    sleep 1;
done
sudo kubeadm join m:6443 --token $master_token --discovery-token-unsafe-skip-ca-verification 

# patch the kubelet to force --resolv-conf=''
sudo sed -i 's#Environment="KUBELET_CONFIG_ARGS=--config=/var/lib/kubelet/config.yaml"#Environment="KUBELET_CONFIG_ARGS=--config=/var/lib/kubelet/config.yaml --resolv-conf=''"#g' /etc/systemd/system/kubelet.service.d/10-kubeadm.conf
sudo systemctl daemon-reload 
sudo systemctl restart kubelet.service

# if it complains that "[ERROR Port-10250]: Port 10250 is in use", kill the process.
# if it complains some file already exist, remove those. [ERROR FileAvailable--etc-kubernetes-pki-ca.crt]: /etc/kubernetes/pki/ca.crt already exists

date
