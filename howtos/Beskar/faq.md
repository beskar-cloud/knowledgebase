# Frequently Asked Questions (FAQ)

## What resources do I need to install beskar cloud?

Our Beskar cloud architecture document comes with [recommended](architecture.md#recommended-hw-specification) and [minimal server specifications](architecture.md#minimal-configuration).

## What versions of openstack does beskar cloud use?

Beskar cloud supports [all current OpenStack versions](https://releases.openstack.org/).

## How to upgrade openstack?

OpenStack cloud version can be easily upgraded component by component by supplying the next version of container images.
OpenStack-helm helm charts are adding with automatic upgrades gracefully as part of bootstrapping including the database schema migrations.
We encourage users to read OpenStack release notes, especially upgrade notes section ([example](https://docs.openstack.org/releasenotes/cinder/yoga.html#upgrade-notes)).

We have so far tested following OpenStack versions:
 * OpenStack Zed
 * OpenStack Wallaby -> OpenStack Yoga upgrade
 * OpenStack Wallaby

## How to upgrade underlying kubernetes?

Kubernetes upgrade procedure could be performed following the [official kubernetes upgrade documentation](https://kubernetes.io/docs/tasks/administer-cluster/cluster-upgrade).

Note that OpenStack-helm and OpenStack-helm-infra helm charts may use deprecated kubernetes resource versions and therefore
we recommend to test kubernetes upgrade while OpenStack is deployed in lab / staging environment before production one.

Our environments are running on Kubernetes `1.24.<last>` version.