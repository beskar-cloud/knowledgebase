# OpenStack orphaned allocation

## TLDR;
After unsuccessful OpenStack VM migration the VM resource allocation may got orphaned, i.e. allocation is claimed but not used by any VM. Hypervisors are not used till the limit.

## How to deal and fix orphaned allocation


### 1. Migration took place
```sh
openstack server migrate --host eli-hda1-016-ostack.priv.cloud.domain.edu  f160ed61-2256-4401-aece-789cb1a3c359
```

### 2. Migration failed, timeout not copied all ephemeral data

```sh
[freznicek@lenovo-t14 ~ 0]$ openstack server show f160ed61-2256-4401-aece-789cb1a3c359 -fjson | grep -E 'status|state|hostname'
  "OS-EXT-SRV-ATTR:hostname": "dark-angel.elasticsearch",
  "OS-EXT-SRV-ATTR:hypervisor_hostname": "eli-hda1-010-ostack.priv.cloud.domain.edu",
  "OS-EXT-STS:power_state": 5,
  "OS-EXT-STS:task_state": none,
  "OS-EXT-STS:vm_state": "stopped",
  "host_status": "UP",
  "status": "SHUTOFF",
```

### 3. target node disk was deleted

```sh
root@eli-hda1-016-ostack $ rm -rf /var/lib/nova/instances/f160ed61-2256-4401-aece-789cb1a3c359
```


### 4. target node seemed to be clean

```sh
$ openstack hypervisor show eli-hda1-016-ostack.priv.cloud.domain.edu -f json
{
  "aggregates": [
	"eli-hda1-ostack.priv.cloud.domain.edu"
  ],
  "cpu_info": {
	"arch": "x86_64",
	"features": [ ... ]
  }
  "current_workload": 0,
  "free_disk_gb": 1760,
  "free_ram_mb": 764303,
  "host_ip": "10.16.108.196",
  "hypervisor_hostname": "eli-hda1-016-ostack.priv.cloud.domain.edu",
  "hypervisor_type": "QEMU",
  "hypervisor_version": 2012000,
  "id": "f3bfbfa8-4dcb-4cf1-b8b3-5b3069870d08",
  "local_gb": 1760,
  "local_gb_used": 0,
  "memory_mb": 772495,
  "memory_mb_used": 8192,
  "running_vms": 0,
  "service_host": "eli-hda1-016-ostack.priv.cloud.domain.edu",
  "service_id": "81d642c7-e12c-4b02-93c1-7314410d0512",
  "state": "up",
  "status": "enabled",
  "users": "1",
  "vcpus": 30,
  "vcpus_used": 0
}
```

### 5. Another VM migration failed

```sh
openstack server migrate --host eli-hda1-016-ostack.priv.cloud.domain.edu  f160ed61-2256-4401-aece-789cb1a3c359
No valid host was found. No valid host found for cold migrate
```

### 6. Placement shows that target hypervisor is not a candidate anymore -> ORPHANED allocation

```sh
[freznicek@lenovo-t14 ~ 0]$ ids=$(openstack allocation candidate list --resource VCPU=30 --resource MEMORY_MB=741376 --resource DISK_GB=1638 -fjson --limit 50 | jq -r '.[]."resource provider"' |  tr '\n' '|')
[freznicek@lenovo-t14 ~ 0]$ openstack hypervisor list | grep -E "${ids%|}" | grep " up "
+--------------------------------------+----------------------------------------+------+---------------+----+
| a9673ac1-6c47-4fbe-a844-a65cd3a3293e | eli-hda2-038-ostack.priv.cloud.domain.edu | QEMU | 10.16.108.218 | up |
+======================================+========================================+======+===============+====+
| b23e4570-fe27-4cf9-99cc-6fe0ee937ba4 | eli-hda2-052-ostack.priv.cloud.domain.edu | QEMU | 10.16.108.232 | up |
+--------------------------------------+----------------------------------------+------+---------------+----+
```

### 7. Identify orphaned allocation

```sh
[freznicek@lenovo-t14 ~ 0]$ openstack resource provider list | grep eli-hda1-016
| f3bfbfa8-4dcb-4cf1-b8b3-5b3069870d08 | eli-hda1-016-ostack.priv.cloud.domain.edu     |         54 | f3bfbfa8-4dcb-4cf1-b8b3-5b3069870d08 | None                 |

[freznicek@lenovo-t14 ~ 130]$ openstack resource provider inventory list f3bfbfa8-4dcb-4cf1-b8b3-5b3069870d08
+----------------+------------------+----------+----------+----------+-----------+--------+--------+
| resource_class | allocation_ratio | min_unit | max_unit | reserved | step_size |  total |   used |
+----------------+------------------+----------+----------+----------+-----------+--------+--------+
+-----------+-----+---+--------+------+---+--------+--------+
| VCPU      | 1.0 | 1 | 30     | 0    | 1 | 30     | 30     |
+===========+=====+===+========+======+===+========+========+
| MEMORY_MB | 1.0 | 1 | 772495 | 8192 | 1 | 772495 | 741376 |
+-----------+-----+---+--------+------+---+--------+--------+
| DISK_GB   | 1.0 | 1 | 1760   | 0    | 1 | 1760   | 1668   |
+-----------+-----+---+--------+------+---+--------+--------+
+----------------+------------------+----------+----------+----------+-----------+--------+--------+
```

### 8. Remove orphaned allocation

```sh
[freznicek@lenovo-t14 ~ 0]$ openstack resource provider show --allocations f3bfbfa8-4dcb-4cf1-b8b3-5b3069870d08
+----------------------+---------------------------------------------------------------------------------------------------------------------------------------+
| Field                | Value                                                                                                                                 |
+----------------------+---------------------------------------------------------------------------------------------------------------------------------------+
+----------------------+---------------------------------------------------------------------------------------------------------------------------------------+
| uuid                 | f3bfbfa8-4dcb-4cf1-b8b3-5b3069870d08                                                                                                  |
+======================+=======================================================================================================================================+
| name                 | eli-hda1-016-ostack.priv.cloud.domain.edu                                                                                                |
+----------------------+---------------------------------------------------------------------------------------------------------------------------------------+
| generation           | 54                                                                                                                                    |
+----------------------+---------------------------------------------------------------------------------------------------------------------------------------+
| root_provider_uuid   | f3bfbfa8-4dcb-4cf1-b8b3-5b3069870d08                                                                                                  |
+----------------------+---------------------------------------------------------------------------------------------------------------------------------------+
| parent_provider_uuid | None                                                                                                                                  |
+----------------------+---------------------------------------------------------------------------------------------------------------------------------------+
| allocations          | {'f160ed61-2256-4401-aece-789cb1a3c359': {'resources': {'VCPU': 30, 'MEMORY_MB': 741376, 'DISK_GB': 1668}, 'consumer_generation': 1}} |
+----------------------+---------------------------------------------------------------------------------------------------------------------------------------+
+----------------------+---------------------------------------------------------------------------------------------------------------------------------------+

[freznicek@lenovo-t14 ~ 0]$ openstack resource provider allocation unset f160ed61-2256-4401-aece-789cb1a3c359
```

### 9. Validate alocation is gone and Placement is saying node is back

```sh
[freznicek@lenovo-t14 ~ 0]$ openstack resource provider show --allocations f3bfbfa8-4dcb-4cf1-b8b3-5b3069870d08
+----------------------+----------------------------------------+
| Field                | Value                                  |
+----------------------+----------------------------------------+
+----------------------+----------------------------------------+
| uuid                 | f3bfbfa8-4dcb-4cf1-b8b3-5b3069870d08   |
+======================+========================================+
| name                 | eli-hda1-016-ostack.priv.cloud.domain.edu |
+----------------------+----------------------------------------+
| generation           | 55                                     |
+----------------------+----------------------------------------+
| root_provider_uuid   | f3bfbfa8-4dcb-4cf1-b8b3-5b3069870d08   |
+----------------------+----------------------------------------+
| parent_provider_uuid | None                                   |
+----------------------+----------------------------------------+
| allocations          | {}                                     |
+----------------------+----------------------------------------+
+----------------------+----------------------------------------+
[freznicek@lenovo-t14 ~ 0]$ openstack resource provider inventory list f3bfbfa8-4dcb-4cf1-b8b3-5b3069870d08
+----------------+------------------+----------+----------+----------+-----------+--------+------+
| resource_class | allocation_ratio | min_unit | max_unit | reserved | step_size |  total | used |
+----------------+------------------+----------+----------+----------+-----------+--------+------+
+-----------+-----+---+--------+------+---+--------+---+
| VCPU      | 1.0 | 1 | 30     | 0    | 1 | 30     | 0 |
+===========+=====+===+========+======+===+========+===+
| MEMORY_MB | 1.0 | 1 | 772495 | 8192 | 1 | 772495 | 0 |
+-----------+-----+---+--------+------+---+--------+---+
| DISK_GB   | 1.0 | 1 | 1760   | 0    | 1 | 1760   | 0 |
+-----------+-----+---+--------+------+---+--------+---+
+----------------+------------------+----------+----------+----------+-----------+--------+------+

[freznicek@lenovo-t14 ~ 0]$ ids=$(openstack allocation candidate list --resource VCPU=30 --resource MEMORY_MB=741376 --resource DISK_GB=1638 -fjson --limit 50 | jq -r '.[]."resource provider"' |  tr '\n' '|')
[freznicek@lenovo-t14 ~ 0]$ openstack hypervisor list | grep -E "${ids%|}" | grep " up "
+--------------------------------------+----------------------------------------+------+---------------+----+
| a9673ac1-6c47-4fbe-a844-a65cd3a3293e | eli-hda2-038-ostack.priv.cloud.domain.edu | QEMU | 10.16.108.218 | up |
+======================================+========================================+======+===============+====+
| b23e4570-fe27-4cf9-99cc-6fe0ee937ba4 | eli-hda2-052-ostack.priv.cloud.domain.edu | QEMU | 10.16.108.232 | up |
+--------------------------------------+----------------------------------------+------+---------------+----+
| f3bfbfa8-4dcb-4cf1-b8b3-5b3069870d08 | eli-hda1-016-ostack.priv.cloud.domain.edu | QEMU | 10.16.108.196 | up |
+--------------------------------------+----------------------------------------+------+---------------+----+
[freznicek@lenovo-t14 ~ 0]$
```


## Resources:
 * https://docs.openstack.org/nova/latest/admin/troubleshooting/orphaned-allocations.html



