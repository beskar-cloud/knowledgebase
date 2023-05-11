# How to migrate VM from OpenStack hypervisor

* Use openstack client from [cloud-toolbox](https://gitlab.ics.muni.cz/cloud/cloud-toolbox) with admin application credentials.
* Stop scheduling VMs to given hypervisor in horizon UI (`Admin -> Hypervisors -> Disable`) or via console `openstack compute service set --disable --disable-reason "${original_hypervisor} maintenance" "${original_hypervisor}" nova-compute`

## Migration of stopped VM (cold migration)


```sh
$ original_hypervisor="c4e-corec-002-ostack.priv.cloud.domain.edu"
$ server_id="8007e7fc-9459-4c71-8d40-0c83c0d79f01"

# 1. list VMs on given hypervisor
$ openstack server list --all-projects --host "${original_hypervisor}"
# 2. check VM state (expected status SHUTOFF)
$ openstack server show "${server_id}"
# 3. Initiate VM migration (status changes to RESIZE and finally to VERIFY_RESIZE)
$ openstack server migrate "${server_id}"
# 4. check VM state (on different hypersisor, expected status VERIFY_RESIZE)
$ openstack server show "${server_id}"
# 5. Confirm VM migration
$ openstack server migrate confirm "${server_id}"
# 6. check VM state (on different hypersisor, expected status SHUTOFF)
$ openstack server show "${server_id}"

```
Notes:
 1. Resize / cold migration is able to transfer ephemeral disks.
 1. When migration is in the process VM is in state `RESIZE`, nova-compute transfers ephemeral data to /var/lib/nova/instances/ of destination hypervisor
```sh
$ openstack server show f160ed61-2256-4401-aece-789cb1a3c359 -fjson | grep -E 'status|state|hostname'
  "OS-EXT-SRV-ATTR:hostname": "dark-angel.elasticsearch",
  "OS-EXT-SRV-ATTR:hypervisor_hostname": "eli-hda1-010-ostack.priv.cloud.domain.edu",
  "OS-EXT-STS:power_state": 4,
  "OS-EXT-STS:task_state": "resize_migrating",
  "OS-EXT-STS:vm_state": "stopped",
  "host_status": "UP",
  "status": "RESIZE",
```

### References
 * https://docs.openstack.org/nova/ussuri/admin/migration.html



## Migration of running VM (live migration)

### the target host unspecified

```sh
$ original_hypervisor="c4e-corec-002-ostack.priv.cloud.domain.edu"
$ server_id="f4387558-4d6a-4aff-8af0-a71f7eefbad6"

# Check your most recent OpenStack Compute API version -> 2.79
$ openstack versions show | grep compute
| brno1       | compute        | 2.0     | SUPPORTED | https://compute.cloud.domain.edu/v2/            | None             | None             |
| brno1       | compute        | 2.1     | CURRENT   | https://compute.cloud.domain.edu/v2.1/          | 2.1              | 2.79             |

# 1. list VMs on given hypervisor
$ openstack server list --all-projects --host "${original_hypervisor}"
# 2. check VM state (expected status ACTIVE)
$ openstack server show "${server_id}"
# 3a. Initiate VM live migration (do not wait till done)
$ openstack --os-compute-api-version=2.79 server migrate --live-migration "${server_id}"
# 3b. Initiate VM live migration (wait till done) ALTERNATIVE
$ openstack --os-compute-api-version=2.79 server migrate --live-migration "${server_id}" --wait
# 4. check VM state (expected status MIGRATING and finally ACTIVE)
$ openstack server show "${server_id}"
```

#### Live migration to any compatible hypervisor may be slightly automated this way
```sh
# low-level part: live-migrate single VM
# --------------------------------------
# ostack_server_migrate_live <server-id>
function ostack_server_migrate_live() {
  local id="$1"
  local regexp="status|hypervisor_hostname|instance_name|task_"
  openstack server show "${id}" -f json | grep -E "${regexp}"
  openstack --os-compute-api-version=2.79 server migrate --live-migration "${id}" --wait
  openstack server show "${id}" -f json | grep -E "${regexp}"
}
# ostack_server_migrate_live f4387558-4d6a-4aff-8af0-abcdefefbad6

# high-level facing part (migration everything off the ics-cored-009)
# -------------------------------------------------------------------
vm_ids=$(openstack server list --host ics-cored-009-ostack.priv.cloud.domain.edu --all-projects | grep ACTIVE | awk '{printf  $2 " "}')
for i_vm in ${vm_ids}; do
  ostack_server_migrate_live $i_vm
  read -p "$i_vm $?, next?" x
done
```

### the target host specified

```sh
$ original_hypervisor="c4e-corec-002-ostack.priv.cloud.domain.edu"
$ target_hypervisor="c4e-corec-001-ostack.priv.cloud.domain.edu"
$ server_id="f4387558-4d6a-4aff-8af0-a71f7eefbad6"

# Check your most recent OpenStack Compute API version -> 2.79
$ openstack versions show | grep compute
| brno1       | compute        | 2.0     | SUPPORTED | https://compute.cloud.domain.edu/v2/            | None             | None             |
| brno1       | compute        | 2.1     | CURRENT   | https://compute.cloud.domain.edu/v2.1/          | 2.1              | 2.79             |

# 1. list VMs on given hypervisor
$ openstack server list --all-projects --host "${original_hypervisor}"
# 2. doublecheck state of target hypervisor - ideally pick hypervisor from same cluster
$ openstack hypervisor show "${target_hypervisor}"
$ openstack server list --all-projects --host "${target_hypervisor}"
# 3. check VM state (expected status ACTIVE)
$ openstack server show "${server_id}"
# 4. Initiate VM live migration
$ openstack --os-compute-api-version=2.79 server migrate --live-migration --host "${target_hypervisor}" "${server_id}"
# 5. check VM state (expected status MIGRATING and finally ACTIVE)
$ openstack server show "${server_id}"

```
### References
 * https://docs.openstack.org/nova/ussuri/admin/live-migration-usage.html shows `openstack server migrate --live "${target_hypervisor}" ...` which is deprecated and problematic as show below:
```sh
$ openstack server migrate --help
usage: openstack server migrate [-h] [--live-migration] [--live <hostname> | --host <hostname>] [--shared-migration | --block-migration] [--disk-overcommit | --no-disk-overcommit] [--wait] <server>

Migrate server to different host. A migrate operation is implemented as a resize operation using the same flavor as the old server. This means that, like resize, migrate works by creating a new server using the same
flavor and copying the contents of the original disk into a new one. As with resize, the migrate operation is a two-step process for the user: the first step is to perform the migrate, and the second step is to either
confirm (verify) success and release the old server, or to declare a revert to release the new server and restart the old one.

positional arguments:
  <server>              Server (name or ID)

optional arguments:
  --live-migration      Live migrate the server. Use the ``--host`` option to specify a target host for the migration which will be validated by the scheduler.
  --live <hostname>     **Deprecated** This option is problematic in that it requires a host and prior to compute API version 2.30, specifying a host during live migration will bypass validation by the scheduler which
                        could result in failures to actually migrate the server to the specified host or over-subscribe the host. Use the ``--live-migration`` option instead. If both this option and ``--live-migration``
                        are used, ``--live-migration`` takes priority.
  --host <hostname>     Migrate the server to the specified host. Requires ``--os-compute-api-version`` 2.30 or greater when used with the ``--live-migration`` option, otherwise requires ``--os-compute-api-version`` 2.56
                        or greater.
...
``` 
 * https://wiki.openstack.org/wiki/OpsGuide-Maintenance-Compute 


## Troubleshooting migrations

### Live migration completes but finally VM is still on such hypervisor

#### libvirtd: operation failed: guest CPU doesn't match specification: missing features: ...

If journal contains following message:

```
libvirtd: 226754: error : virNetClientProgramDispatchError:172 : operation failed: guest CPU doesn't match specification: missing features: ibpb
```
after live migration attempt, you need to shutdown the VM and apply cold migration instead.

More reading on:
 * https://bbs.archlinux.org/viewtopic.php?id=237553
 * https://www.intel.com/content/www/us/en/developer/articles/technical/software-security-guidance/technical-documentation/indirect-branch-predictor-barrier.html


### Live migration fails to finish, leaving VM server migrated but database claims it is not migrated

Sometimes VM live migration times out (default timeout is 102400 seconds).
To avoid live migration timeouts you may try:
 1. Pause migrated VM while being migrated (`ssh root@<original-hypervisor> virsh suspend <original-vm-domain-name-or-id>`), unpause once live migration finishes (`ssh root@<new-hypervisor> virsh resume <new-vm-domain-name-or-id>`)
 1. [Set live-migration custom timeout and on-timeout action](https://specs.openstack.org/openstack/nova-specs/specs/pike/approved/live-migration-per-instance-timeout.html) to wait shorter time and/or define migration successfull on migration timeout
 1. [Correct migration state in nova database](https://access.redhat.com/solutions/2070503):

```sh
# source openstack client credentials (as environment variables)
source ~/conf/admin.sh.inc

# list instance on incorrect host
$ openstack server list --all-projects --host ics-cored-013-ostack.priv.cloud.domain.edu
+--------------------------------------+--------+--------+-------------------------------------------------------+-------+------------------------+                                                                       
| ID                                   | Name   | Status | Networks                                              | Image | Flavor                 |                                                                       
+--------------------------------------+--------+--------+-------------------------------------------------------+-------+------------------------+                                                                       
| a5d39f2e-3e3c-4e58-bdb1-c98b9520c16b | fenrir | ACTIVE | auto_allocated_network=192.168.4.143, 147.251.124.111 |       | standard.20core-128ram |                                                                       
+--------------------------------------+--------+--------+-------------------------------------------------------+-------+------------------------+                                                                       

# VM is not on the host
ssh root@ics-cored-013-ostack 'virsh list --all'
 Id   Jméno   Stav
--------------------

# VM is found on hypervisor ics-cored-005-ostack.priv.cloud.domain.edu
$ ostack_kvm_locate_vm a5d39f2e-3e3c-4e58-bdb1-c98b9520c16b
...
ics-cored-005-ostack.priv.cloud.domain.edu
  /etc/libvirt/qemu/instance-0000017f.xml:  <uuid>a5d39f2e-3e3c-4e58-bdb1-c98b9520c16b</uuid>
  /etc/libvirt/qemu/instance-0000017f.xml:      <entry name='serial'>a5d39f2e-3e3c-4e58-bdb1-c98b9520c16b</entry>
  /etc/libvirt/qemu/instance-0000017f.xml:      <entry name='uuid'>a5d39f2e-3e3c-4e58-bdb1-c98b9520c16b</entry>
  /etc/libvirt/qemu/instance-0000017f.xml:      <source protocol='rbd' name='prod-ephemeral-vms/a5d39f2e-3e3c-4e58-bdb1-c98b9520c16b_disk.config'>
  /etc/libvirt/qemu/instance-0000017f.xml:      <log file='/var/lib/nova/instances/a5d39f2e-3e3c-4e58-bdb1-c98b9520c16b/console.log' append='off'/>
  /etc/libvirt/qemu/instance-0000017f.xml:      <log file='/var/lib/nova/instances/a5d39f2e-3e3c-4e58-bdb1-c98b9520c16b/console.log' append='off'/>
...

# VM state before migration
$ openstack server show a5d39f2e-3e3c-4e58-bdb1-c98b9520c16b
+-------------------------------------+---------------------------------------------------------------+
| Field                               | Value                                                         |
+-------------------------------------+---------------------------------------------------------------+
| OS-DCF:diskConfig                   | AUTO                                                          |
| OS-EXT-AZ:availability_zone         | brno1                                                         |
| OS-EXT-SRV-ATTR:host                | ics-cored-013-ostack.priv.cloud.domain.edu                       |
| OS-EXT-SRV-ATTR:hypervisor_hostname | ics-cored-013-ostack.priv.cloud.domain.edu                       |
| OS-EXT-SRV-ATTR:instance_name       | instance-0000017f                                             |
| OS-EXT-STS:power_state              | NOSTATE                                                       |
| OS-EXT-STS:task_state               | None                                                          |
| OS-EXT-STS:vm_state                 | active                                                        |
| OS-SRV-USG:launched_at              | 2020-03-04T18:22:21.000000                                    |
| OS-SRV-USG:terminated_at            | None                                                          |
| accessIPv4                          |                                                               |
| accessIPv6                          |                                                               |
| addresses                           | auto_allocated_network=192.168.4.143, 147.251.124.111         |
| config_drive                        | True                                                          |
| created                             | 2019-05-06T14:52:07Z                                          |
| flavor                              | standard.20core-128ram (864eb488-1477-4b68-aec4-832c8e48df55) |
| hostId                              | 9264b5810168d1c1e6008f1cda96666937a55df49d078d0e5333747f      |
| id                                  | a5d39f2e-3e3c-4e58-bdb1-c98b9520c16b                          |
| image                               |                                                               |
| key_name                            | ll35                                                          |
| name                                | fenrir                                                        |
| progress                            | 99                                                            |
| project_id                          | cee625e6adde4904933f19efe795e416                              |
| properties                          |                                                               |
| security_groups                     | name='default'                                                |
|                                     | name='fenrir'                                                 |
| status                              | ACTIVE                                                        |
| updated                             | 2021-08-10T18:38:36Z                                          |
| user_id                             | 174bcfbe5b524f3baf72fa58ae1f637b                              |
| volumes_attached                    | id='c76741b7-3346-4c31-8803-bf72f1a14a26'                     |
|                                     | id='7529bebe-c4b8-43ef-833b-674272730a57'                     |
|                                     | id='d178f009-4c52-4b9c-9a78-b7b23b55a070'                     |
+-------------------------------------+---------------------------------------------------------------+


ssh root@db-ostack...
  # dump current database state
  migration_dir=/root/freznicek/db-migration
  mkdir -p ${migration_dir}/before ${migration_dir}/after
  mysqldump nova > ${migration_dir}/before/nova.sql
  mysqldump nova_api > ${migration_dir}/nova_api.sql

  # doublecheck that VM instance is in the database
  [root@db-ostack production ~]$ mysql nova -e "select node,host,uuid,vm_state,task_state,power_state,deleted from instances where uuid='a5d39f2e-3e3c-4e58-bdb1-c98b9520c16b';"
  +-----------------------------------------+-----------------------------------------+--------------------------------------+----------+------------+-------------+---------+
  | node                                    | host                                    | uuid                                 | vm_state | task_state | power_state | deleted |
  +-----------------------------------------+-----------------------------------------+--------------------------------------+----------+------------+-------------+---------+
  | ics-cored-013-ostack.priv.cloud.domain.edu | ics-cored-013-ostack.priv.cloud.domain.edu | a5d39f2e-3e3c-4e58-bdb1-c98b9520c16b | active   | NULL       |           0 |       0 |
  +-----------------------------------------+-----------------------------------------+--------------------------------------+----------+------------+-------------+---------+

  # rewrite host, node and power_state values associated with VM instance
  [root@db-ostack production ~]$ mysql nova -e "update instances set host='ics-cored-005-ostack.priv.cloud.domain.edu',node='ics-cored-005-ostack.priv.cloud.domain.edu',power_state=1 where uuid='a5d39f2e-3e3c-4e58-bdb1-c98b9520c16b' and deleted = 0;"

  # validate VM instance in the database is corrected
  [root@db-ostack production ~]$ mysql nova -e "select node,host,uuid,vm_state,task_state,power_state,deleted from instances where uuid='a5d39f2e-3e3c-4e58-bdb1-c98b9520c16b';"
  +-----------------------------------------+-----------------------------------------+--------------------------------------+----------+------------+-------------+---------+
  | node                                    | host                                    | uuid                                 | vm_state | task_state | power_state | deleted |
  +-----------------------------------------+-----------------------------------------+--------------------------------------+----------+------------+-------------+---------+
  | ics-cored-005-ostack.priv.cloud.domain.edu | ics-cored-005-ostack.priv.cloud.domain.edu | a5d39f2e-3e3c-4e58-bdb1-c98b9520c16b | active   | NULL       |           1 |       0 |
  +-----------------------------------------+-----------------------------------------+--------------------------------------+----------+------------+-------------+---------+

# validate VM instance is corrected in openstack client detail
$ openstack server show a5d39f2e-3e3c-4e58-bdb1-c98b9520c16b
+-------------------------------------+---------------------------------------------------------------+
| Field                               | Value                                                         |
+-------------------------------------+---------------------------------------------------------------+
| OS-DCF:diskConfig                   | AUTO                                                          |
| OS-EXT-AZ:availability_zone         | brno1                                                         |
| OS-EXT-SRV-ATTR:host                | ics-cored-005-ostack.priv.cloud.domain.edu                       |
| OS-EXT-SRV-ATTR:hypervisor_hostname | ics-cored-005-ostack.priv.cloud.domain.edu                       |
| OS-EXT-SRV-ATTR:instance_name       | instance-0000017f                                             |
| OS-EXT-STS:power_state              | Running                                                       |
| OS-EXT-STS:task_state               | None                                                          |
| OS-EXT-STS:vm_state                 | active                                                        |
| OS-SRV-USG:launched_at              | 2020-03-04T18:22:21.000000                                    |
| OS-SRV-USG:terminated_at            | None                                                          |
| accessIPv4                          |                                                               |
| accessIPv6                          |                                                               |
| addresses                           | auto_allocated_network=192.168.4.143, 147.251.124.111         |
| config_drive                        | True                                                          |
| created                             | 2019-05-06T14:52:07Z                                          |
| flavor                              | standard.20core-128ram (864eb488-1477-4b68-aec4-832c8e48df55) |
| hostId                              | 9d0e410bbbb80ac9020904b6f235a245aa93e93e7a0f8fc7cde473af      |
| id                                  | a5d39f2e-3e3c-4e58-bdb1-c98b9520c16b                          |
| image                               |                                                               |
| key_name                            | ll35                                                          |
| name                                | fenrir                                                        |
| progress                            | 99                                                            |
| project_id                          | cee625e6adde4904933f19efe795e416                              |
| properties                          |                                                               |
| security_groups                     | name='default'                                                |
|                                     | name='fenrir'                                                 |
| status                              | ACTIVE                                                        |
| updated                             | 2021-08-10T18:38:36Z                                          |
| user_id                             | 174bcfbe5b524f3baf72fa58ae1f637b                              |
| volumes_attached                    | id='c76741b7-3346-4c31-8803-bf72f1a14a26'                     |
|                                     | id='7529bebe-c4b8-43ef-833b-674272730a57'                     |
|                                     | id='d178f009-4c52-4b9c-9a78-b7b23b55a070'                     |
+-------------------------------------+---------------------------------------------------------------+
```
 4. Doublecheck that VM after migration and correction use exact number of volumes and volumes are provided from destination hypervisor only


#### References
 * https://access.redhat.com/solutions/2070503
 * https://specs.openstack.org/openstack/nova-specs/specs/pike/approved/live-migration-per-instance-timeout.html
