# Replication controller experiments

## Getting started
The two directories `listening_server` and `kill_worker` contain a pair of apps that are designed to measure how long it takes Kubernetes to restart an app after it crashes. Both of these have a Dockerfile to be built into containers to run on Kubernetes.

To test them locally install `minikube` and `docker-engine` and follow the below steps.

```sh
minikube start

# shares local docker with that running on minikube
eval $(minikube docker-env)

# build metric app
cd listening_server
docker build . -t metric-collection

# build kill worker
cd kill_worker
docker build . -t kill-worker

# start metric collection app and expose a service
kubectl run metric --image=metric-collection:latest --image-pull-policy=Never
kubectl expose deployment metric --type=NodePort --port=5000

# start kill worker
kubectl run worker --image=kill-worker:latest --image-pull-policy=Never

# get url of metric service
minikube service hello-minikube --url
# example output > http://192.168.39.239:30368
```

When you visit the URL produced by the last step, you should see startup times being collected from the kill worker.


Sources:

 - [Installing Kubernetes with Minikube - Kubernetes](https://kubernetes.io/docs/setup/learning-environment/minikube/)
 - [linux - How to use local docker images with Minikube? - Stack Overflow](https://stackoverflow.com/questions/42564058/how-to-use-local-docker-images-with-minikube)
