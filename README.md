# Honours Project repository

Repository containing any code relevant to my honours project (undergraduate thesis) at the University of Edinburgh. The project aim initially was to look at the security aspects of network slicing in the 5G core network, but is currently in a state of flux and this repository will be updated as and when the goal settles down.

## Getting started
The two directories `listening_server` and `malicious_suicide` contain a pair of apps that are designed to measure how long it takes Kubernetes to restart an app after it crashes. Both of these have a Dockerfile to be built into containers to run on Kubernetes.

To test them locally install `minikube` and `docker-engine` and follow the below steps.

```sh
minikube start

# shares local docker with that running on minikube
eval $(minikube docker-env)

# build metric app
cd listening_server
docker build . -t metric-collection

# build suicidal app
cd malicious_suicide
docker build . -t suicidal-app

# start metric collection app and expose a service
kubectl run metric --image=metric-collection:latest --image-pull-policy=Never
kubectl expose deployment metric --type=NodePort --port=5000

# start suicidal app
kubectl run suicide --image=suicidal-app:latest --image-pull-policy=Never

# get url of metric service
minikube service hello-minikube --url
# example output > http://192.168.39.239:30368
```

When you visit the URL produced by the last step, you should see startup times being collected from the suicidal app.


Sources:
[Installing Kubernetes with Minikube - Kubernetes](https://kubernetes.io/docs/setup/learning-environment/minikube/)
[linux - How to use local docker images with Minikube? - Stack Overflow](https://stackoverflow.com/questions/42564058/how-to-use-local-docker-images-with-minikube)




./listening_server:
app.py
Dockerfile
__pycache__
requirements.txt
templates

./listening_server/templates:
index.html

./malicious_suicide:
Dockerfile
requirements.txt
suicide.py
