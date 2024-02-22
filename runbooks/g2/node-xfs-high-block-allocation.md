# Node High Inode Allocation

**Initial runbook version.**

## Problem

The alert fires when the filesystem is running out of available inodes (xfs blocks).

## Analysis

Note the `instance` and `mountpoint` labels from the alert. You can graph the
usage history of this filesystem with the following query in the OpenShift web
console:

```promql
node_filesystem_files_free{
  instance="<value of instance label from alert>",
  mountpoint="<value of mountpoint label from alert>"
}
```

You can also open a debug session on the node and use the standard Linux
utilities to locate the source of the usage:

```shell
$ MOUNT_POINT='<value of mountpoint label from alert>'
$ NODE_NAME='<value of instance label from alert>'

$ oc debug "node/$NODE_NAME"
$ df -hi "/host/$MOUNT_POINT"
```

Note that in many cases a filesystem running out of inodes will still have
available storage. Running out of inodes is often caused by many many small
files being created by an application.

## Resolution

The number of inodes allocated to a filesystem is usually based on the storage
size. You may be able to solve the problem, or buy time, by increasing size of
the storage volume. Otherwise, determine the application that is creating large
numbers of files and adjust its configuration or provide it dedicated storage.

## References
 * [Community Runbook](https://runbooks.prometheus-operator.dev/runbooks/node/nodefilesystemfilesfillingup/)
