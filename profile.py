kube_description= \
"""
IGNORE THE BELOW DESCRIPTION, COPIED FROM OTHER PROFILE

This profile deploys the following components:
1. Kubernetes, multi-node clusters using kubeadm, using docker.

It takes around 5-10 minutes to complete the whole procedure.
   Detail about kubernetes deployment please refer to [kubernetes documentation page](https://kubernetes.io/docs/setup/independent/create-cluster-kubeadm/)
   Detail about Sockshop microservices please refer to [sock shop demo microservice](https://microservices-demo.github.io/)
   Detail about Jaeger tracing can be found [here](https://github.com/jaegertracing/jaeger)

Out of convenience, it is also instantiated with:
1. kubernetes dashboard installed.
2. helm, to install kubernetes "packages"
3. jid and jq, for json format parsing.

"""
kube_instruction= \
"""
IGNORE THE BELOW INSTRUCTIONS, COPIED FROM OTHER PROFILE

After 5-10 minutes, the endpoint and credential will be printed at the tail of /mnt/extra/deploy.log.
You can also print it manually using the commands below:

```bash
    export KUBEHOME="/mnt/extra/kube/"
    export KUBECONFIG=$KUBEHOME/admin.conf
    jaeger_port=`kubectl --namespace=jaeger get svc -o go-template='{{range .items}}{{if eq .metadata.name "jaeger-query"}}{{index .spec.ports 0 "nodePort"}}{{"\n"}}{{end}}{{end}}'`
    jaeger_endpoint=`kubectl get endpoints --all-namespaces |grep jaeger-query|awk '{print $3}'`
    sockshop_endpoint=`kubectl get endpoints --all-namespaces |grep front-end|awk '{print $3}'`
    dashboard_endpoint=`kubectl get endpoints --all-namespaces |grep dashboard|awk '{print $3}'`
    dashboard_credential=`kubectl -n kube-system describe secret $(kubectl -n kube-system get secret | grep admin-user | awk '{print $1}') |grep token: | awk '{print $2}'`

    echo "Kubernetes is ready at: http://localhost:8001/api/v1/namespaces/kube-system/services/https:kubernetes-dashboard:/proxy/#!/login"
    echo "sockshop will be ready in 5 minutes at: http://localhost:30001"
    echo "jaeger will be ready in 5 minutes at: http://localhost:${jaeger_port}"

    # optional address
    echo "Or, another access option (jaeger's localhost port does not work on my windows port forwarding somehow)"
    echo "Jaeger endpoint: $jaeger_endpoint"
    echo "sockshop endpoint: $sockshop_endpoint"
    echo "kubernetes dashboard endpoint: $dashboard_endpoint"
    # dashboard credential
    echo "And this is the dashboard credential: $dashboard_credential"
```

You can find the deploy script at:
   /mnt/extra/master.sh for master node
   /mnt/extra/slave.sh for slave node

The deployment log is kept at /mnt/extra/deploy.log

###Known issues
1. the yaml scripts of sockshop deployment is kept in the same repo as this profile, it is not mirrored with the official website. Mainly because of two reasons:
    - there are some resource limit problem making the deployment somehow failed and I have not yet have time to find out why. I simply remove those resource limit.
    - I plan to submit a PR of this profile to its official webpage later, but I need sometime to clean the code to make it published. But I have no time to do it yet.
2. There is a known DNS problem in the Java microservices: even though it inheri the host node's resolv.conf with the "Cluster_first" policy, Java application in the container will directly bypass the /etc/resolv.conf and leading to in cluster domain name not found. This profile resolve it by explicitly set the resolv_conf to be empty using kubelet command line arguements (note that here involves another bug in kubernetes that using kubelet config.yaml can not make the resolv.conf as empty, simplly because when the ResolvConf=="" it will use the default which is /etc/resolv.conf).
3. This profile uses Ubuntu 16.04 instead of 18.04 because kubernetes does not have a bionic source yet, this will be upgraded when Kubernetes bionic is ready.
4. Sometimes the endpoint info is not generated in the deploy.log just because at the time of running, the endpoint was not really ready yet. At that time, just wait a little bit more minutes and run the commands above.
5. The sockshop microservice seems to be not very reliable somehow sometimes.
"""


# Import the Portal object.
import geni.portal as portal
# Import the ProtoGENI library.
import geni.rspec.pg as pg
# Import the Emulab specific extensions.
import geni.rspec.emulab as emulab
import geni.rspec.igext as IG
import geni.rspec.pg as RSpec

# TODO: Is 12GB enough storage?
# TODO: Write master/slave scripts

##################### Unneeded? #########################
# bs0 = kube_m.Blockstore('bs0', '/mnt/extra')
# bs0.size = '200GB'
# bs0.placement = 'NONSYSVOL'
# kube_m.addService(pg.Install('https://gitlab.flux.utah.edu/licai/emulab-profile/raw/master/private-profiles/kubernetes/kubernetes.tar.gz','/mnt/extra/'))
#     bs = kube_s.Blockstore('bs'+str(i), '/mnt/extra')
    # bs.size = '200GB'
    # bs.placement = 'NONSYSVOL'
    # kube_s.addService(pg.Install('https://gitlab.flux.utah.edu/licai/emulab-profile/raw/master/private-profiles/kubernetes/kubernetes.tar.gz','/mnt/extra/'))
# #########################################################

# Create a portal object,
pc = portal.Context()

# leared this from: https://www.emulab.net/portal/show-profile.php?uuid=f6600ffd-e5a7-11e7-b179-90e2ba22fee4
pc.defineParameter("computeNodeCount", "Number of slave/compute nodes",
                   portal.ParameterType.INTEGER, 1)
pc.defineParameter("useVMs", "Whether to use virtual machines or raw PCs",
                   portal.ParameterType.BOOLEAN, True)
params = pc.bindParameters()

# Create a Request object to start building the RSpec.
request = pc.makeRequestRSpec()


#rspec = RSpec.Request()
tour = IG.Tour()
tour.Description(IG.Tour.TEXT,kube_description)
tour.Instructions(IG.Tour.MARKDOWN,kube_instruction)
request.addTour(tour)

# Node kube-server
if params.useVMs:
    kube_m = request.XenVM('m')
    kube_m.cores = 4
    kube_m.ram = 1024 * 8
else:
    kube_m = request.RawPC('m')
    kube_m.hardware_type = 'd430'
kube_m.disk_image = 'urn:publicid:IDN+emulab.net+image+emulab-ops:UBUNTU16-64-STD'
#kube_m.disk_image = 'urn:publicid:IDN+emulab.net+image+emulab-ops:UBUNTU18-64-STD'
kube_m.Site('Site 1')
iface0 = kube_m.addInterface('interface-0')
kube_m.addService(pg.Install('https://github.com/notexactlyawe/honours-project/archive/master.tar.gz', '/local/'))
kube_m.addService(pg.Execute(shell="bash", command="/local/honours-project-master/scripts/master.sh"))

slave_ifaces = []
for i in range(1,params.computeNodeCount+1):
    if params.useVMs:
        kube_s = request.XenVM('s'+str(i))
        kube_s.cores = 4
        kube_s.ram = 1024 * 8
    else:
        kube_s = request.RawPC('s'+str(i))
        kube_s.hardware_type = 'd430'
    kube_s.disk_image = 'urn:publicid:IDN+emulab.net+image+emulab-ops:UBUNTU16-64-STD'
    #kube_s.disk_image = 'urn:publicid:IDN+emulab.net+image+emulab-ops:UBUNTU18-64-STD'
    kube_s.Site('Site 1')
    slave_ifaces.append(kube_s.addInterface('interface-'+str(i)))
    kube_s.addService(pg.Install('https://github.com/notexactlyawe/honours-project/archive/master.tar.gz', '/local/'))
    kube_s.addService(pg.Execute(shell="bash", command="/local/honours-project-master/scripts/slave.sh"))

# Link link-m
link_m = request.Link('link-0')
link_m.Site('undefined')
link_m.addInterface(iface0)
for i in range(params.computeNodeCount):
    link_m.addInterface(slave_ifaces[i])

# Print the generated rspec
pc.printRequestRSpec(request)
