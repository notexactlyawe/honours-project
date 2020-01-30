# Honours Project repository

Repository containing any code relevant to my honours project (undergraduate thesis) at the University of Edinburgh. The project aim initially was to look at the security aspects of network slicing in the 5G core network, but is currently in a state of flux and this repository will be updated as and when the goal settles down.

Each folder within this top level contains a specific experiment to do with this project and a README for that experiment.

## Experiments

### `replication_controller`

This folder contains code that attempts to measure the time it takes for each loop of the replication controller in Kubernetes to run. It does this by measuring the time it takes to restart a Python script that keeps killing itself.
