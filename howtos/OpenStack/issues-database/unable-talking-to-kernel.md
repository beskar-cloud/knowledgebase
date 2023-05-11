# libvirtd internal error: Child process (/usr/sbin/tc filter add dev tap... parent ffff: protocol all u32 match u32 0 0 police rate 250000kbps burst 250000kb mtu 64kb drop flowid :1) unexpected exit status 2: RTNETLINK answers: Invalid argument

## Symptoms

* VM ends in ERROR state and alert `NovaVirtualMachineStatusFails - Nova reports unexpected VM provisioning status for more than 30 minutes` fires
  * in trace it is visible string: `internal error: Child process (/usr/sbin/tc filter add dev tap6882089e-22 parent ffff: protocol all u32 match u32 0 0 police rate 250000kbps burst 250000kb mtu 64kb drop flowid :1) unexpected exit status 2: RTNETLINK answers: Invalid argument
We have an error talking to the kernel`

* hypervisor shows in journal
```
led 04 15:41:22 ics-cored-009-ostack.priv.cloud.domain.edu libvirtd[14520]: 14533: error : virCommandWait:2613 : internal error: Child process (/usr/sbin/tc filter add dev tapbe375aa3-4c parent ffff: protocol all u32 match u32 0 0 police rate 250000kbps burst 250000kb mtu 64kb drop flowid :1) unexpected exit status 2: RTNETLINK answers: Invalid argument
led 04 16:02:32 ics-cored-009-ostack.priv.cloud.domain.edu libvirtd[14520]: 14520: error : virNetSocketReadWire:1803 : End of file while reading data: Input/output error
led 04 16:03:17 ics-cored-009-ostack.priv.cloud.domain.edu libvirtd[14520]: 14520: error : virNetSocketReadWire:1803 : End of file while reading data: Input/output error
led 04 16:13:42 ics-cored-009-ostack.priv.cloud.domain.edu libvirtd[14520]: 14533: error : virNetClientProgramDispatchError:172 : internal error: Child process (/usr/sbin/tc filter add dev tap6882089e-22 parent ffff: protocol all u32 match u32 0 0 police rate 250000kbps burst 250000kb mtu 64kb drop flowid :1) unexpected exit status 2: RTNETLINK answers: Invalid argument
We have an error talking to the kernel
```
## Resolution

One of the approaches should be functional, often the last one.

### Approach A (restart libvirtd and redeploy infra state)

```sh
# on hypervisor
service libvirtd restart
puppet agent -t -v
```

### Approach B (upgrade, restart libvirtd and redeploy infra state)

```sh
# on hypervisor
yum update -x puppet5-release
service libvirtd restart
puppet agent -t -v
```


### Approach C (upgrade, migrate all VMs out of hypervisor, reboot and redeploy infra state)

1. On hypervisor upgrade to latest packages
```sh
yum update -x puppet5-release
```

2. Mark node as disabled (on your laptop)
```sh
openstack compute service set --disable --disable-reason "freznicek:ics-cored-009-ostack.priv.cloud.domain.edu servers in ERROR maintenance/reboot" ics-cored-009-ostack.priv.cloud.domain.edu nova-compute
```

3. Live migrate all VMs out of node (on your laptop)

Follow [howtos/OpenStack/vm-instance-migration.md](/howtos/OpenStack/vm-instance-migration.md#live-migration-to-any-compatible-hypervisor-may-be-slightly-automated-this-way) and live migrate all VMs out of hypervisor

4. Reboot hypervisor and redeploy (on hypervisor)
```sh
reboot
puppet agent -t -v
```

5. Enable hypervisor (on your laptop)
```sh
openstack compute service set --enable ics-cored-009-ostack.priv.cloud.domain.edu nova-compute
```


6. Test creation of the VM on the hypervisor (on your laptop)
```sh
openstack --os-compute-api-version 2.74 server create --image debian-10-x86_64 --flavor standard.tiny --network 8e303e86-7b8e-4d17-8e87-976417d3a804 --key-name freznicek-admin --availability-zone brno1:ics-cored-009-ostack.priv.cloud.domain.edu freznicek-test
openstack server show c9bab6fd-6290-4786-b3c8-8f8a2a1ee4de -f json
```
If VM starts OK then problem is gone.

7. Recovering original failed VM (in state ERROR)

```sh
FAILED_VM_ID=274bb318-a7e1-4d97-b419-7fe35dda24b5
nova reset-state  $FAILED_VM_ID             # reset to RESET state
nova reset-state --active $FAILED_VM_ID     # reset to ACTIVE state, but VM is not running
openstack server show $FAILED_VM_ID -f json
openstack server stop $FAILED_VM_ID         # ACTIVE -> SHUTOFF
openstack server show $FAILED_VM_ID -f json
openstack server start $FAILED_VM_ID        # SHUTOFF -> ACTIVE, VM is running
openstack server show $FAILED_VM_ID -f json # doublecheck state in ostack via API and on HV node
```

If you face following error message:
```
ERROR (CommandError): You must provide a user name/id (via --os-username, --os-user-id, env[OS_USERNAME] or env[OS_USER_ID]) or an auth token (via --os-token).
```
you use nova client that don't support v3applicationcredential. You have to
use following env variables:

```
export OS_AUTH_URL=https://identity.cloud.domain.edu/v3
export OS_PROJECT_NAME="admin"
export OS_USER_DOMAIN_NAME="default"
export OS_PROJECT_DOMAIN_ID="default"
export OS_USERNAME="admin"
export OS_PASSWORD="*********"
export OS_REGION_NAME="brno1"
export OS_INTERFACE=public
export OS_COMPUTE_API_VERSION=2.79
export OS_IDENTITY_API_VERSION=3
export OS_VOLUME_API_VERSION=3
```

Replace value of OS_PASSWORD with actual admin password.


## References:
* https://access.redhat.com/solutions/6087111
