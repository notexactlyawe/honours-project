# Collected data from experiments

This directory contains all datasets collected as part of the honours project. It uses [Git LFS](https://git-lfs.github.com/) to avoid bloating the repository. The filename format is as follows:

```
YYYY-MM-DD.<EXP>.<ID>.<DB>

EXP - Experiment type (HPA, Replication etc)
ID  - Unique number given date and EXP to identify multiple datasets from the same day
DB  - Database used to collect data (eg sqlite3)
```

Each file has the conditions of recording documented below.

## Files

### `2020-02-18.hpa.1.sqlite3`

 - Description: `temp.db` as recorded by cpu-control pod, first experiment
 - RepoHash: ad5cbf32d4377fed9353f5e45525ca8782e97346
 - POWDER Start: Feb 18, 2020 4:44 PM
 - POWDER Finish: Feb 18, 2020 8:44 PM
 - Hardware: Raw d430 master + 1 d430 slave
 - Time snapshotted: Tue Feb 18 20:39:26 GMT 2020
 - Notes: SSH sessions on master until 17:05 and from 20:00-20:09

### `2020-04-08.hpa.1.sqlite3`

 - Description: First experiment with load, metrics-server metric-resolution=15s
 - RepoHash: 9e3294e2fb05f9438771c31d84da16e973513cb7
 - POWDER Start: Apr 8, 2020 2:42 PM
 - POWDER Finish: Apr 10, 2020 6:42 AM
 - First downscale: "2020-04-08T15:25:00"
 - Downscale period: 30 minutes
 - Hardware: Raw d710 master + 6 d710 slaves
 - Time snapshotted: 2020-04-08 19:55:00
 - Notes: shared powder session with 2020-04-09.hpa.1.sqlite3

### `2020-04-09.hpa.1.sqlite3`

 - Description: second experiment with load, metrics-server metric-resolution default (60s)
 - RepoHash: 9e3294e2fb05f9438771c31d84da16e973513cb7
 - POWDER Start: Apr 8, 2020 2:42 PM
 - POWDER Finish: Apr 10, 2020 6:42 AM
 - First downscale: "2020-04-08T22:34:00"
 - Downscale period: 90 minutes
 - Hardware: Raw d710 master + 6 d710 slaves
 - Time snapshotted: 2020-04-09 12:04:00
 - Notes: shared powder session with 2020-04-08.hpa.1.sqlite3

## Hardware definitions

Just in case the Emulab wiki page goes away.

### d430s (from [Emulab wiki](https://gitlab.flux.utah.edu/emulab/emulab-devel/-/wikis/Utah%20Cluster#d430s))
There are 160 d430 nodes (pc701-pc860) consisting of:

 - [Dell Poweredge R430](http://i.dell.com/sites/doccontent/shared-content/data-sheets/en/Documents/Dell-PowerEdge-R430-Spec-Sheet.pdf)
 - Two 2.4 GHz 64-bit 8-Core Xeon E5-2630v3 processors, 8.0 GT/s, 20 MB
 - cache, VT-x, VT-d and EPT support
 - 64 GB 2133 MT/s DDR4 RAM (8 x 8GB modules)
 - 2-4 Intel i350 GbE NICs for experimental use
 - 2-4 Intel X710 10 GbE NICs for experimental use
 - 200 GB 6Gbps SATA SSD, 2 x 1 TB 7200 RPM 6 Gbps SATA disks.

[More details about the d430s.](https://gitlab.flux.utah.edu/emulab/emulab-devel/-/wikis/Utah-Cluster/d430s)

### d710s (from [Emulab wiki](https://gitlab.flux.utah.edu/emulab/emulab-devel/-/wikis/Utah%20Cluster#d710s))
There are 160 d710 PC nodes (pc401-pc560) consisting of:

 - [Dell Poweredge R710](http://www.dell.com/downloads/global/products/pedge/en/server-poweredge-r710-specs-en.pdf)
 - 2.4 GHz 64-bit Quad Core Xeon E5530 "Nehalem" processor, 5.86 GT/s bus
 - speed, 8 MB L3 cache, VT support
 - 12 GB 1066 MHz DDR2 RAM (6 x 2GB modules)
 - 4 Broadcom NetXtreme II BCM5709 rev C GbE NICs builtin to motherboard
 - 2 Broadcom NetXtreme II BCM5709 rev C GbE NICs in dual-port PCIe x4
 - expansion card (one NIC is the control net)
 - 2x 250GB 7200 rpm SATA disks

[More details about the d710s.](https://gitlab.flux.utah.edu/emulab/emulab-devel/-/wikis/Utah-Cluster/d710s)
