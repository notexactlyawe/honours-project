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
