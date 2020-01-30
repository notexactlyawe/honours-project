docker build kill_worker -t kill-worker
kubectl delete deployment hello-foo
kubectl rollout restart deployment/metrics
# magic sleep to wait for metrics to restart
sleep 3
kubectl run hello-foo --image=kill-worker:latest --image-pull-policy=Never
