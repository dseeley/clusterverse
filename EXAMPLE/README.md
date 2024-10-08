# clusterverse-example  &nbsp; [![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause) ![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen.svg)
This is an example of a deployment of [clusterverse](https://github.com/dseeley/clusterverse) - _the full-lifecycle cloud infrastructure cluster management project, using Ansible._

_**Please refer to the full [README.md](https://github.com/dseeley/clusterverse/blob/master/README.md) in the main [clusterverse](https://github.com/dseeley/clusterverse) repository.**_ 

## Contributing
Contributions are welcome and encouraged.  Please see [CONTRIBUTING.md](https://github.com/dseeley/clusterverse/blob/master/CONTRIBUTING.md) for details.

## Requirements
+ Ansible >= 9.3.0
+ Python >= 3.10


---
## Invocation examples: _deploy_, _scale_, _repair_
The `cluster.yml` sub-role immutably deploys a cluster from the config defined above.  If it is run again it will do nothing.  If the cluster_vars are changed (e.g. add a host), the cluster will reflect the new variables (e.g. a new host will be added to the cluster).

### AWS:
```
ansible-playbook cluster.yml -e buildenv=sandbox -e clusterid=testid -e cloud_type=aws -e region=eu-west-1 --vault-id=sandbox@.vaultpass-client.py
ansible-playbook cluster.yml -e buildenv=sandbox -e clusterid=testid -e cloud_type=aws -e region=eu-west-1 --vault-id=sandbox@.vaultpass-client.py --tags=clusterverse_clean -e clean=_all_
ansible-playbook cluster.yml -e buildenv=sandbox -e clusterid=test_aws_euw1 --vault-id=sandbox@.vaultpass-client.py
ansible-playbook cluster.yml -e buildenv=sandbox -e clusterid=test_aws_euw1 --vault-id=sandbox@.vaultpass-client.py --tags=clusterverse_clean -e clean=_all_
```
### GCP:
```
ansible-playbook cluster.yml -e buildenv=sandbox -e clusterid=testid -e cloud_type=gcp -e region=europe-west1 --vault-id=sandbox@.vaultpass-client.py
ansible-playbook cluster.yml -e buildenv=sandbox -e clusterid=testid -e cloud_type=gcp -e region=europe-west1 --vault-id=sandbox@.vaultpass-client.py --tags=clusterverse_clean -e clean=_all_
ansible-playbook cluster.yml -e buildenv=sandbox -e clusterid=test_gcp_euw1 --vault-id=sandbox@.vaultpass-client.py
ansible-playbook cluster.yml -e buildenv=sandbox -e clusterid=test_gcp_euw1 --vault-id=sandbox@.vaultpass-client.py --tags=clusterverse_clean -e clean=_all_
```
### Azure:
```
ansible-playbook cluster.yml -e buildenv=sandbox -e cloud_type=azure -e region=westeurope --vault-id=sandbox@.vaultpass-client.py
ansible-playbook cluster.yml -e buildenv=sandbox -e cloud_type=azure -e region=westeurope --vault-id=sandbox@.vaultpass-client.py --tags=clusterverse_clean -e clean=_all_
```
### libvirt:
```
ansible-playbook cluster.yml -e buildenv=sandbox -e cloud_type=libvirt --vault-id=sandbox@.vaultpass-client.py
ansible-playbook cluster.yml -e buildenv=sandbox -e cloud_type=libvirt --vault-id=sandbox@.vaultpass-client.py --tags=clusterverse_clean -e clean=_all_
```
### ESXi (free):
```
ansible-playbook cluster.yml -e buildenv=sandbox -e cloud_type=esxifree --vault-id=sandbox@.vaultpass-client.py
ansible-playbook cluster.yml -e buildenv=sandbox -e cloud_type=esxifree --vault-id=sandbox@.vaultpass-client.py --tags=clusterverse_clean -e clean=_all_
```

### Mandatory command-line variables:
+ `-e buildenv=<sandbox>` - The environment (dev, stage, etc), which must be an attribute of `cluster_vars` (i.e. `{{cluster_vars[build_env]}}`)
+ `-e cloud_type=[aws|gcp|azure|libvirt|esxifree]` - The cloud type.

### Optional extra variables:
+ `-e app_name=<nginx>` - Normally defined in `/cluster_defs/`.  The name of the application cluster (e.g. 'couchbase', 'nginx'); becomes part of cluster_name
+ `-e app_class=<proxy>` - Normally defined in `/cluster_defs/`.  The class of application (e.g. 'database', 'webserver'); becomes part of the fqdn (if so defined as part of `dns_nameserver_zone`)
+ `-e omit_singleton_hosttype_from_hostname=[true|false]` - When there is only one hosttype in the cluster, whether to omit the hosttype from the hostname, (e.g. bastion-dev-node-a0 -> bastion-dev-a0).  DO NOT use when there is a chance you will need it in future.
+ `-e clean=[current|retiring|redeployfail|_all_]` - Deletes VMs in `lifecycle_state`, or `_all_` (all states), as well as networking and security groups
+ `-e pkgupdate=[always|on_create]` - Upgrade the OS packages (not good for determinism).  `on_create` only upgrades when creating the VM for the first time.
+ `-e reboot_on_package_upgrade=true` - After updating packages, performs a reboot on all nodes.
+ `-e static_journal=true` - Creates /var/log/journal directory, which will keep a permanent record of journald logs in systemd machines (normally ephemeral)
+ `-e wait_for_dns=false` - Does not wait for DNS resolution
+ `-e create_gcp_network=true` - Create GCP network and subnetwork (probably needed if creating from scratch and using public network)
+ `-e delete_gcp_network_on_clean=true` - Delete GCP network and subnetwork when run with `-e clean=_all_`
+ `-e cluster_vars_override='{"sandbox.hosttype_vars.sys.vms_by_az":{"b":1,"c":1,"d":0}}'` - Ability to override cluster_vars dictionary elements from the command line.  NOTE: there must be NO SPACES in this string.

### Tags
+ `clusterverse_clean`: Deletes all VMs and security groups (also needs `-e clean=[current|retiring|redeployfail|_all_]` on command line)
+ `clusterverse_create`: Creates only EC2 VMs, based on the hosttype_vars values in `/cluster_defs/`
+ `clusterverse_config`: Updates packages, sets hostname, adds hosts to DNS


---

## Invocation examples: _redeploy_
The `redeploy.yml` sub-role will completely redeploy the cluster; this is useful for example to upgrade the underlying operating system version, or changing the disk sizes.

### AWS:
```
ansible-playbook redeploy.yml -e buildenv=sandbox -e cloud_type=aws -e region=eu-west-1 --vault-id=sandbox@.vaultpass-client.py -e canary=none
```
### GCP:
```
ansible-playbook redeploy.yml -e buildenv=sandbox -e cloud_type=gcp -e region=europe-west1 --vault-id=sandbox@.vaultpass-client.py -e canary=none
```
### Azure:
```
ansible-playbook redeploy.yml -e buildenv=sandbox -e cloud_type=azure -e region=westeurope --vault-id=sandbox@.vaultpass-client.py -e canary=none
```

### Mandatory command-line variables:
+ `-e buildenv=<sandbox>` - The environment (dev, stage, etc), which must be an attribute of `cluster_vars` defined in `group_vars/<clusterid>/cluster_vars.yml`
+ `-e canary=['start', 'finish', 'filter', 'none', 'tidy']` - Specify whether to start, finish or filter a canary redeploy (or 'none', to redeploy the whole cluster in one command).  See below (`-e canary_filter_regex`) for `canary=filter`.
+ `-e redeploy_scheme=<subrole_name>` - The scheme corresponds to one defined in `roles/clusterverse/redeploy`

### Extra variables:
+ `-e canary_tidy_on_success=[true|false]` - Whether to run the tidy (remove the replaced VMs and DNS) on successful redeploy 
+ `-e canary_filter_regex='^.*-test-sysdisks.*$'` - Sets the regex pattern used to filter the target hosts by their hostnames - mandatory when using `canary=filter`
+ `-e myhosttypes="master,slave"`- In redeployment you can define which host type you like to redeploy. If not defined it will redeploy all host types
