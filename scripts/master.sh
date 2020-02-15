#!/bin/bash
#set -u
#set -x

SCRIPTDIR=$(dirname "$0")
WORKINGDIR='/local/repository'
username=$(id -nu)
usergid=$(id -ng)
experimentid=$(hostname|cut -d '.' -f 2)
projectid=$usergid

sudo chown ${username}:${usergid} ${WORKINGDIR}/ -R
cd $WORKINGDIR
# Redirect output to log file
exec >> ${WORKINGDIR}/deploy.log
exec 2>&1

KUBEHOME="${WORKINGDIR}/kube/"
DEPLOY_CONFIG="${WORKINGDIR}/hpa_controller/deploy/"
mkdir -p $KUBEHOME && cd $KUBEHOME
# TODO this file isn't in the tarball (confusion)
export KUBECONFIG=$KUBEHOME/admin.conf

cd $WORKINGDIR
# Don't think we need to clone this
#git clone git@gitlab.flux.utah.edu:licai/emulab-profile.git
# Install sock shop?
#pushd $KUBEHOME
#git clone https://github.com/microservices-demo/microservices-demo
#popd

# install kubernetes
curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add
sudo apt-add-repository "deb http://apt.kubernetes.io/ kubernetes-xenial main"
echo "deb http://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee -a /etc/apt/sources.list.d/kubernetes.list
#sudo apt-add-repository "deb http://apt.kubernetes.io/ kubernetes-bionic main"
#echo "deb http://apt.kubernetes.io/ kubernetes-bionic main" | sudo tee -a /etc/apt/sources.list.d/kubernetes.list
sudo apt-get update
sudo apt-get -y install build-essential libffi-dev python python-dev  \
python-pip automake autoconf libtool indent vim tmux ctags

# learn from this: https://blog.csdn.net/yan234280533/article/details/75136630
# more info should see: https://kubernetes.io/docs/setup/independent/create-cluster-kubeadm/
sudo apt-get -y install  docker-engine kubelet kubeadm kubectl kubernetes-cni golang-go jq
sudo docker version
sudo swapoff -a
sudo kubeadm init --pod-network-cidr=192.168.0.0/16

# result will be like:  kubeadm join 155.98.36.111:6443 --token i0peso.pzk3vriw1iz06ruj --discovery-token-ca-cert-hash sha256:19c5fdee6189106f9cb5b622872fe4ac378f275a9d2d2b6de936848215847b98

# https://github.com/kubernetes/kubernetes/issues/44665
sudo cp /etc/kubernetes/admin.conf $KUBEHOME/
sudo chown ${username}:${usergid} $KUBEHOME/admin.conf

sudo kubectl create -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/k8s-manifests/kube-flannel-rbac.yml
sudo kubectl create -f https://github.com/coreos/flannel/raw/master/Documentation/kube-flannel.yml

# use this to enable autocomplete
source <(kubectl completion bash)

# kubectl get nodes --kubeconfig=${KUBEHOME}/admin.conf -s https://155.98.36.111:6443
# Install dashboard: https://github.com/kubernetes/dashboard
#sudo kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/master/src/deploy/recommended/kubernetes-dashboard.yaml
sudo kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v1.10.1/src/deploy/recommended/kubernetes-dashboard.yaml
 
# run the proxy to make the dashboard portal accessible from outside
sudo kubectl proxy  --kubeconfig=${KUBEHOME}/admin.conf  &

# https://github.com/kubernetes/dashboard/wiki/Creating-sample-user
#kubectl create -f $DEPLOY_CONFIG/create-cluster-role-binding-admin.yaml  
#kubectl create -f $DEPLOY_CONFIG/create-service-account-admin-uesr-dashboard.yaml
# to print the token, use this cmd below to paste into the browser.
# kubectl -n kube-system describe secret $(kubectl -n kube-system get secret | grep admin-user | awk '{print $1}') |grep token: | awk '{print $2}'

# jid for json parsing.
export GOPATH=${WORKINGDIR}/go/gopath
mkdir -p $GOPATH
export PATH=$PATH:$GOPATH/bin
sudo go get -u github.com/simeji/jid/cmd/jid
sudo go build -o /usr/bin/jid github.com/simeji/jid/cmd/jid

# install helm in case we needs it.
wget https://storage.googleapis.com/kubernetes-helm/helm-v2.9.1-linux-amd64.tar.gz
tar xf helm-v2.9.1-linux-amd64.tar.gz
sudo cp linux-amd64/helm /usr/local/bin/helm

helm init
# https://docs.helm.sh/using_helm/#role-based-access-control
kubectl create serviceaccount --namespace kube-system tiller
kubectl create clusterrolebinding tiller-cluster-rule --clusterrole=cluster-admin --serviceaccount=kube-system:tiller
kubectl patch deploy --namespace kube-system tiller-deploy -p '{"spec":{"template":{"spec":{"serviceAccount":"tiller"}}}}'      
helm init --service-account tiller --upgrade

source <(helm completion bash)

# Install metrics-server for HPA
helm install stable/metrics-server --name metrics-server --namespace metrics

# Wait till the slave nodes get joined and update the kubelet daemon successfully
nodes=(`ssh -o StrictHostKeyChecking=no ${username}@ops.emulab.net "{ /usr/testbed/bin/node_list -p -e ${projectid},${experimentid}; }"`)
node_cnt=${#nodes[@]}
joined_cnt=$(( `kubectl get nodes |wc -l` - 1 ))
while [ $node_cnt -ne $joined_cnt ]
do 
    joined_cnt=$(( `kubectl get nodes |wc -l` - 1 ))
    sleep 1
done

# install experiment deployments
kubectl apply -f $DEPLOY_CONFIG

# install microservices app
#kubectl apply -f  ${WORKINGDIR}/emulab-profile/private-profiles/kubernetes/microservices-yaml/manifests/sock-shop-ns.yaml 
#sleep 5s
#kubectl apply -f  ${WORKINGDIR}/emulab-profile/private-profiles/kubernetes/microservices-yaml/manifests
#sleep 5s
#kubectl apply -f  ${WORKINGDIR}/emulab-profile/private-profiles/kubernetes/microservices-yaml/manifests-jaeger

#$ kubectl get endpoints --all-namespaces |grep jaeger-query|awk '{print $3}'
#192.168.1.14:16686
#$ kubectl get endpoints --all-namespaces |grep front-end|awk '{print $3}'
#192.168.1.5:8079
#$ kubectl get endpoints --all-namespaces |grep dashboard|awk '{print $3}'
#192.168.0.2:8443
#jaeger_access=`kubectl get endpoints -n jaeger  -o go-template='{{range .items}}{{if eq .metadata.name "jaeger-query"}} {{index .subsets 0 "addresses" 0 "ip" }}|{{index .subsets 0 "ports" 0 "port"}} {{end}}{{end}}' | tr "|" ":"`

#jaeger_endpoint=`kubectl get endpoints --all-namespaces |grep jaeger-query|awk '{print $3}'`
#sockshop_endpoint=`kubectl get endpoints --all-namespaces |grep front-end|awk '{print $3}'`
dashboard_endpoint=`kubectl get endpoints --all-namespaces |grep dashboard|awk '{print $3}'`
dashboard_credential=`kubectl -n kube-system describe secret $(kubectl -n kube-system get secret | grep admin-user | awk '{print $1}') |grep token: | awk '{print $2}'`
#jaeger_port=`kubectl --namespace=jaeger get svc -o go-template='{{range .items}}{{if eq .metadata.name "jaeger-query"}}{{index .spec.ports 0 "nodePort"}}{{"\n"}}{{end}}{{end}}'`

echo "Kubernetes is ready at: http://localhost:8001/api/v1/namespaces/kube-system/services/https:kubernetes-dashboard:/proxy/#!/login"
#echo "sockshop will be ready in 5 minutes at: http://localhost:30001"
#echo "jaeger will be ready in 5 minutes at: http://localhost:${jaeger_port}"

# optional address
#echo "Or, another access option (jaeger's localhost port does not work on my windows port forwarding somehow)"
#echo "Jaeger endpoint: $jaeger_endpoint"
#echo "sockshop endpoint: $sockshop_endpoint"
echo "kubernetes dashboard endpoint: $dashboard_endpoint"
# dashboard credential
echo "And this is the dashboard credential: $dashboard_credential"

# to know how much time it takes to instantiate everything.
date
