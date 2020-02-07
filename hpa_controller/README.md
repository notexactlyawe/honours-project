# HPA controller experiments

The two directories `busy_worker` and `metric_server` contain two python applications that are designed to work together to measure the time it takes for a Horizontal Pod Autoscaler control loop to execute. `busy_worker` sends a heartbeat message to `metric_server` and gets back a CPU percentage that it should be using. `metric_server` tracks how many `busy_worker`s are alive and controls the CPU usage accordingly.

The aim of the two applications is to cause some state to change every iteration of the HPA control loop. By measuring when that state is resolved by the control loop (pods created/destroyed) it should be possible to measure how much load the kubernetes cluster is experiencing, assuming the control loop has 'at least' semantics in its timing.

## Getting started

Open three terminals. The first will be to run the `metric_server` and the other two will run `busy_worker`s. If desired, a fourth terminal with `top` can also be used to see the CPU usage of each `busy_worker`. The below commands assume that you are running in a Python 3.8 environment with the requirements from the respective directories' `requirements.txt` installed.

``` sh
# Terminal 1 - start metric-server
# set cpu target for HPA controller
export K8s_CPU_TARGET="0.3"

# start server
cd metric_server
python app.py

##################
# Terminal 2/3
# set address of metric_server
export METRICS_SERVICE_HOST=localhost
export METRICS_SERVICE_PORT=5000

# start busy_worker
cd busy_worker
python worker.py

##################
# Terminal 4 (optional)
# run top to view CPU usage of pods
top
```

After starting these workers up, you will see that stopping them and restarting them will change the CPU that each of them use.

## Running on Minikube

Whilst these applications will work on their own, to test them out with the autoscaler, you'll need to run them on a Kubernetes cluster. This part of the getting started assumes you have Minikube and docker installed.

### Starting Minikube

The server will attempt to make workers be spun up and then destroyed on alternate iterations of the loop. To make this happen, some settings need to be changed on the `controller-manager`. It's worth noting that if using Kubernetes 1.18+ this will no longer be needed and the changes can be made in the YAML.

On top of this, another setting is needed to make `metrics-server` run properly, which is needed for the autoscaler to function.

``` sh
minikube start \
    --extra-config=controller-manager.horizontal-pod-autoscaler-downscale-stabilization=10s \
    --extra-config=kubelet.authentication-token-webhook=true
```

### Deploying `metrics-server`

The Horizontal Pod Autoscaler relies on an optional Kubernetes service called `metrics-server`. Execute the following commands to get it set up.

``` sh
git clone https://github.com/kubernetes-sigs/metrics-server
cd metrics-server
kubectl create -f deploy/kubernetes
```

For troubleshooting refer to the [GitHub repository](https://github.com/kubernetes-sigs/metrics-server).

### Building Docker imagees.

From the `hpa_controller` folder (the root relative to this README):

``` sh
eval $(minikube docker-env)
docker build busy_worker/ -t busy-worker
docker build metric_server/ -t cpu-control
```

### Starting experiment

``` sh
kubectl create -f server-and-autoscale.yaml
minikube service cpucontrol --url
# eg http://192.168.39.4:32284 
```

Going to the URL given by `minikube service` will show you the status of the `cpu-control` component.

If anything goes wrong, or you want to restart the experiment, delete all components with `kubectl delete -f server-and-autoscale.yaml`.

Sources:
[docker - How do I ssh into the VM for Minikube? - Stack Overflow](https://stackoverflow.com/questions/38870277/how-do-i-ssh-into-the-vm-for-minikube)
[kubectl - Horizontal pod autoscaling in Kubernetes - Stack Overflow](https://stackoverflow.com/questions/50469985/horizontal-pod-autoscaling-in-kubernetes)
[kubernetes-sigs/metrics-server - GitHub](https://github.com/kubernetes-sigs/metrics-server)
