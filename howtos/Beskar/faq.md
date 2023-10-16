# Frequently Asked Questions (FAQ)

## What resources do I need to install beskar cloud?

Our Beskar cloud architecture document comes with [recommended](architecture.md#recommended-hw-specification) and [minimal server specifications](architecture.md#minimal-configuration).

## What versions of openstack does beskar cloud use?

Beskar cloud supports [all current OpenStack versions](https://releases.openstack.org/).

## How to upgrade openstack?

OpenStack cloud version can be easily upgraded component by component by supplying the next version of container images (provided by 
[openstack/openstack-helm-images](https://github.com/openstack/openstack-helm-images) and [openstack/loci](https://github.com/openstack/loci)).
OpenStack-helm helm charts are adding with automatic upgrades gracefully as part of bootstrapping including the database schema migrations.
We encourage users to read OpenStack release notes, especially upgrade notes section ([example](https://docs.openstack.org/releasenotes/cinder/yoga.html#upgrade-notes)).

We have so far tested following OpenStack versions:
 * OpenStack Zed
 * OpenStack Wallaby -> OpenStack Yoga upgrade
 * OpenStack Wallaby

OpenStack minor/patch upgrades are likely driven by bugfixes published upstream. Typically few times each year.


## How to upgrade underlying kubernetes?

Kubernetes upgrade procedure could be performed following the [official kubernetes upgrade documentation](https://kubernetes.io/docs/tasks/administer-cluster/cluster-upgrade).

Note that OpenStack-helm and OpenStack-helm-infra helm charts may use deprecated kubernetes resource versions and therefore
we recommend to test kubernetes upgrade while OpenStack is deployed in lab / staging environment before production one.

Our environments are running on vanilla Kubernetes `1.24` version. We recommend to upgrade to latest patch release (`v1.24.17` as of 2023-10-16) and stay there.


## How to perform backup and disaster recovery?

### Kubernetes

As discussed in [Beskar-cloud architecture](architecture.md), kubernetes controlplane should consist of three or five master nodes running etcd database.
Although etcd is designed to recover from temporary failures it is wise to periodically snapshot etcd state independently on each controplane server file system
as etcd snapshot is best approach of recovering kubernetes cluster state. See [etcd DR article](https://etcd.io/docs/v3.5/op-guide/recovery/) for more details.

### OpenStack

Beskar-cloud uses HA Galera mariadb cluster out of the box relying on [beskar-cloud/openstack-helm-infra/mariadb](https://github.com/beskar-cloud/openstack-helm-infra/tree/main/mariadb) helm chart.
Although it is unlikely to loose all database instances, we recommend to periodically backup OpenStack database to an external / offsite storage.
OpenStack database backup can be easily done with [beskar-cloud/mariadb-s3-backup](https://github.com/beskar-cloud/mariadb-s3-backup) tool to a S3 bucket.
It is wise to actually perform and document recovery operation *before* you actually need it.

## How to troubleshoot infrastructure?

### Kubernetes
 * https://kubernetes.io/docs/tasks/debug/debug-cluster/
 * https://www.redhat.com/sysadmin/kubernetes-troubleshooting
 * https://komodor.com/learn/kubernetes-troubleshooting-the-complete-guide/

### OpenStack
 * https://wiki.openstack.org/wiki/OpsGuide-Network-Troubleshooting
 * https://access.redhat.com/documentation/en-us/red_hat_openstack_platform/16.2/html/logging_monitoring_and_troubleshooting_guide/troubleshooting

### Flux CD
 * https://fluxcd.io/flux/cheatsheets/troubleshooting/

