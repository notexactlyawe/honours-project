# HPA controller experiments

The two directories `busy_worker` and `metric_server` contain two python applications that are designed to work together to measure the time it takes for a Horizontal Pod Autoscaler control loop to execute. `busy_worker` sends a heartbeat message to `metric_server` and gets back a CPU percentage that it should be using. `metric_server` tracks how many `busy_worker`s are alive and controls the CPU usage accordingly.

The aim of the two applications is to cause some state to change every iteration of the HPA control loop. By measuring when that state is resolved by the control loop (pods created/destroyed) it should be possible to measure how much load the kubernetes cluster is experiencing, assuming the control loop has 'at least' semantics in its timing.

## Getting started

TBD
