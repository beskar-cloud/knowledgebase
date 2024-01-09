# Ceph storage monitor quorum low / lost

## Problem

There is low or lost ceph monitor quorum.
Ceph monitors are the user facing components, so users may not be able to communicate with ceph itself.

## Analysis
 * Doublecheck whether your ceph is maintained by yourself or other team.
 * Find details on how many ceph monitors are available.
   * using any container having mounted ceph credentials for instance rook-ceph-operator and issue `ceph status`
```sh
[freznicek@lenovo-t14 ~ 0]$ kubectl get cephclusters --all-namespaces
NAMESPACE            NAME                 DATADIRHOSTPATH   MONCOUNT   AGE    PHASE       MESSAGE                          HEALTH        EXTERNAL
rook-ceph-external   rook-ceph-external   /var/lib/rook                192d   Connected   Cluster connected successfully   HEALTH_WARN   true
[freznicek@lenovo-t14 ~ 130]$ kubectl -n rook-ceph logs --tail=1000  rook-ceph-operator-769c9c4864-pd645 | grep 'ceph status' | tail -1
2023-08-28 14:17:35.427321 D | exec: Running command: ceph status --format json --connect-timeout=15 --cluster=rook-ceph-external --conf=/var/lib/rook/rook-ceph-external/rook-ceph-external.config --name=client.healthchecker --keyring=/var/lib/rook/rook-ceph-external/client.healthchecker.keyring
[freznicek@lenovo-t14 ~ 0]$ kubectl -n rook-ceph exec -it rook-ceph-operator-769c9c4864-pd645 bash
[rook@rook-ceph-operator-769c9c4864-pd645 /]$ ceph status  --connect-timeout=15 --cluster=rook-ceph-external --conf=/var/lib/rook/rook-ceph-external/rook-ceph-external.config --name=client.healthchecker --keyring=/var/lib/rook/rook-ceph-external/client.healthchecker.keyring
  cluster:
    id:     b16*****-****-****-****-*******0e958
    health: HEALTH_WARN
            1202 pgs not deep-scrubbed in time
            1163 pgs not scrubbed in time
            2 pools have too many placement groups

  services:
    mon: 3 daemons, quorum mon001-cl3,mon002-cl3,mon003-cl3 (age 11d)
    mgr: mon003-cl3(active, since 8d), standbys: mon001-cl3, mon002-cl3
    mds: 2/2 daemons up, 1 standby
    osd: 2436 osds: 2435 up (since 10d), 2363 in (since 10d); 2 remapped pgs
    rgw: 48 daemons active (3 hosts, 1 zones)

  data:
    volumes: 2/2 healthy
    pools:   44 pools, 9873 pgs
    objects: 2.32G objects, 8.6 PiB
    usage:   14 PiB used, 15 PiB / 29 PiB avail
    pgs:     47797/40680866370 objects misplaced (0.000%)
             9762 active+clean
             100  active+clean+scrubbing+deep
             9    active+clean+scrubbing
             2    active+remapped+backfilling

  io:
    client:   164 KiB/s rd, 87 MiB/s wr, 16 op/s rd, 80 op/s wr
    recovery: 8.0 MiB/s, 2 objects/s
```
 * Check why are not the non-available ceph monitors restarted. Use golden `kubectl describe` on ceph monitor pods.


## Resolution
 * Restart the non-available ceph monitors.
 * Doublecheck that ceph monitors are back available and alert stopped firing.

## References
 * 
