# Honours Project repository

Repository containing any code relevant to my honours project (undergraduate thesis) at the University of Edinburgh. The project aim initially was to look at the security aspects of network slicing in the 5G core network, but is currently in a state of flux and this repository will be updated as and when the goal settles down.

This repository acts as the backing repository for a POWDER profile (see the [POWDER docs][http://docs.powderwireless.net/creating-profiles.html#(part._repo-based-profiles)])).

## POWDER configuration guide

TODO

## Experiments

The below folders each contain code for a specific experiment to do with this project and a README for that experiment.

### `replication_controller`

This folder contains code that attempts to measure the time it takes for each loop of the replication controller in Kubernetes to run. It does this by measuring the time it takes to restart a Python script that keeps killing itself.

### `hpa_controller`

The Horizontal Pod Autoscaler (HPA) is a kubernetes controller that will create/destroy pods based on their CPU usage. This experiment aims to detect the time it takes for the HPA to run its control loop by measuring the time it takes for a new pod to be created/old pod to die. By measuring this, hopefully information about the Kubernetes cluster that wasn't otherwise available will be revealed.
