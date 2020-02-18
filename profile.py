kube_description= \
"""
This profile deploys the following components:
1. Kubernetes, multi-node clusters using kubeadm, using docker.
2. Kubernetes [metrics-server](https://github.com/kubernetes-sigs/metrics-server)
3. The HPA controller experiments contained in [notexactlyawe/honours-project](https://github.com/notexactlyawe/honours-project)

It takes around 10 minutes to complete the whole procedure.
   Detail about kubernetes deployment please refer to [kubernetes documentation page](https://kubernetes.io/docs/setup/independent/create-cluster-kubeadm/)

Out of convenience, it is also instantiated with:
1. kubernetes dashboard installed.
2. helm, to install kubernetes "packages"
3. jid and jq, for json format parsing.

"""
kube_instruction= \
"""
This profile will clone [notexactlyawe/honours-project](https://github.com/notexactlyawe/honours-project) into `local/repository` on the machine and run the install scripts specified in `/local/repository/scripts`. Instructions for cloning this profile to create your own can be found at the above repository.

The install scripts will send their output to `/local/repository/deploy.log` on both master and slave so installation can be monitored and debugged by running `tail -f /local/repository/deploy.log`.

Parameters:
 - computeNodeCount: the number of slave nodes
 - useVMs: True - use XenVMs for nodes, False - use rawPCs (d430s)

Known issues:
 - The nodes don't run DHCP to get public IPs when using VMs
"""

# Import the Portal object.
import geni.portal as portal
# Import the ProtoGENI library.
import geni.rspec.pg as pg
# Import the Emulab specific extensions.
import geni.rspec.emulab as emulab
import geni.rspec.igext as IG
import geni.rspec.pg as RSpec

# Create a portal object,
pc = portal.Context()

# leared this from: https://www.emulab.net/portal/show-profile.php?uuid=f6600ffd-e5a7-11e7-b179-90e2ba22fee4
pc.defineParameter("computeNodeCount", "Number of slave/compute nodes",
                   portal.ParameterType.INTEGER, 1)
pc.defineParameter("useVMs", "Use virtual machines (true) or raw PCs (false)",
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
# kube_m.disk_image = 'urn:publicid:IDN+emulab.net+image+emulab-ops:UBUNTU16-64-STD'
kube_m.disk_image = 'urn:publicid:IDN+emulab.net+image+emulab-ops:UBUNTU18-64-STD'
kube_m.Site('Site 1')
iface0 = kube_m.addInterface('interface-0')
kube_m.addService(pg.Execute(shell="bash", command="/local/repository/scripts/master.sh"))

slave_ifaces = []
for i in range(1,params.computeNodeCount+1):
    if params.useVMs:
        kube_s = request.XenVM('s'+str(i))
        kube_s.cores = 4
        kube_s.ram = 1024 * 8
    else:
        kube_s = request.RawPC('s'+str(i))
        kube_s.hardware_type = 'd430'
    # kube_s.disk_image = 'urn:publicid:IDN+emulab.net+image+emulab-ops:UBUNTU16-64-STD'
    kube_s.disk_image = 'urn:publicid:IDN+emulab.net+image+emulab-ops:UBUNTU18-64-STD'
    kube_s.Site('Site 1')
    slave_ifaces.append(kube_s.addInterface('interface-'+str(i)))
    kube_s.addService(pg.Execute(shell="bash", command="/local/repository/scripts/slave.sh"))

# Link link-m
link_m = request.Link('link-0')
link_m.Site('undefined')
link_m.addInterface(iface0)
for i in range(params.computeNodeCount):
    link_m.addInterface(slave_ifaces[i])

if params.useVMs:
    pool = IG.AddressPool("ext_ips", params.computeNodeCount + 1)
    request.addResource(pool)

# Print the generated rspec
pc.printRequestRSpec(request)
