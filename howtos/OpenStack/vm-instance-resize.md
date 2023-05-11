# VM instance resize

## Change VM flavor

1. Stop the VM `openstack server stop <SERVER-ID>`
1. Resize VM's flavor `openstack server resize --flavor <FLAVOR-ID> <SERVER-ID>`
1. Confirm/Rollback resize process `openstack server resize confirm <SERVER-ID>`
1. Start VM `openstack server start <SERVER-ID>`

```sh
# resizing transcript
SERVER_ID=66dcc5c1-81dd-4ea1-9daa-472f57c36767

openstack server show -f json "${SERVER_ID}"
openstack server stop "${SERVER_ID}"

# wait until SHUTOFF
openstack server show -f json "${SERVER_ID}"

# list flavors
openstack flavor list | grep ssd-ephem-5
FLAVOR_ID=6c1a91ab-c889-4a22-b6b8-9561663c2d51 # flavor name:hpc.12core-64ram-ssd-ephem-500
openstack server resize --flavor "${FLAVOR_ID}" "${SERVER_ID}"

# wait until migration is done, status turned into VERIFY_RESIZE
# migration can take couple of minutes (indicated by status RESIZE)
openstack server show -f json "${SERVER_ID}" | grep -E 'ssd-ephem-5|"name": |status|task_state|vm_state|host'

# confirm resize
openstack server resize confirm "${SERVER_ID}"

# wait until migration is done, status turned into SHUTOFF
openstack server show -f json "${SERVER_ID}" | grep -E 'ssd-ephem-5|"name": |status|task_state|vm_state|host'

# start VM
openstack server start "${SERVER_ID}"

# on Hypervisor doublecheck that VM is booting well
virsh console <domid/domname>
```
Note: Resize / cold migration is able to transfer ephemeral disks.

### References
* https://docs.openstack.org/nova/train/user/resize.html
* new flavors https://gitlab.ics.muni.cz/cloud/hiera/-/merge_requests/1601

