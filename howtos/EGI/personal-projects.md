# Beskar-cloud personal projects support

## Definitions

Personal project is free-tier OpenStack project with limited quota primarily used IaaS OpenStack cloud playground.
Personal projects are granted for people with particular identity eduperson_entitlement. ([`urn:mace:egi.eu:goc.egi.eu:105599G0:CESNET-MCC:Site+Administrator@egi.eu` example](https://github.com/beskar-cloud/cloud-entities/blob/644e121423bf380922592d47f00de5ed7a5f4ed6/environments/dev-beskar/openstack/global-static-identity-mappings/egi_eu_mapping-gsi-mapping.yaml#L15-L32)).
Personal projects have fixed and immutable cloud quota.
Personal projects are periodically cleaned-up (resources stopped and removed).

## High-level overview

1. OIDC federated OpenStack IaaS cloud with [Keystone mapped plug-in](https://docs.openstack.org/keystone/latest/api/keystone.auth.plugins.mapped.html)
2. Patched Keystone. There are basically two patch sets:
   * a] extended functionality of Keystone mapped plugin
   * b] Increased OpenStack Keystone project name length limitation
3. Introspection [ESACO proxy](https://github.com/indigo-iam/esaco) linked with Keystone
4. Use any way of managing OpenStack entities, especially projects, (service) users, roles and mappings preferably in CI/CD pipeline. See [cloud-entities example](https://github.com/beskar-cloud/cloud-entities).
5. (Optional) Additional ansible playbooks running in CI/CD in order to get following features:
   * OpenStack quota propagation to personal projects
   * OpenStack personal project life-cycle management
   * EGI appliances propagation

All personal projects are created under the defined parent project (using hierarchical manner of OpenStack Keystone projects).
```
* egi_eu                  # EGI domain
  * personal-projects     # umbrella parent project on top of all personal projects
    * abcd@egi.eu         # personal project granted for EGI identity abcd@egi.eu
    * ...                 # ...
    * dcba@egi.eu         # ...
  * group-projects        # umbrella parent project on top of all group projects
    * ...                 # group projects
```

## F.A.Q

### Can we get all necessary patches upstream?

This is ongoing task:
 * 2a] patch set has [issue](https://bugs.launchpad.net/keystone/+bug/2047641) and not yet accepted [PR](https://review.opendev.org/c/openstack/keystone/+/904397).
 * 2b] patch set is DB increment and has [issue](https://bugs.launchpad.net/keystone/+bug/2069960) only atm.
 * 2b] keystone pull-request is ongoing.
  * 2b] How to apply:

```sql
-- we are touching keystone DB
USE keystone;
-- list keystone.project structure
DESCRIBE project;
-- increase max. length of openstack project upto 96 characters
ALTER TABLE project MODIFY COLUMN name varchar(96);
-- list updated keystone.project structure, A/B test with the one above
DESCRIBE project;
```

### Is it possible to define list of managers for personal projects based on the entitlements only?

Yes, this is possible.

See explicit [example](https://github.com/beskar-cloud/cloud-entities/blob/644e121423bf380922592d47f00de5ed7a5f4ed6/environments/dev-beskar/openstack/global-static-identity-mappings/egi_eu_mapping-gsi-mapping.yaml#L46-L64) for more details.

TODO: more automated way.

### Is it possible to define specific quotas for all personal projects?

Yes, possible and automated already.

Although OpenStack does not support nested quotas out of the box we found the solution based on above hierarchical scheme.

Workflow of quota propagation is automated within [ansible playbook `nested-quota-propagation`](https://github.com/beskar-cloud/cloud-entities/blob/main/ci/ansible/nested-quota-propagation.yml).

Configuration of the feature consist of:
 * [tagging `personal-projects` umbrella project with tag `project_nested_quota_propagation.enable=true`](https://github.com/beskar-cloud/cloud-entities/blob/644e121423bf380922592d47f00de5ed7a5f4ed6/environments/dev-beskar/openstack/projects-quotas-acls/egi_eu/personal-projects.yaml#L13)
 * definition of custom personal projects quotas within umbrella project, [example](https://github.com/beskar-cloud/cloud-entities/blob/644e121423bf380922592d47f00de5ed7a5f4ed6/environments/dev-beskar/openstack/projects-quotas-acls/egi_eu/personal-projects.yaml#L15-L16)
 * definition of parent project inside [`nested-quota-propagation`](https://github.com/beskar-cloud/cloud-entities/blob/main/ci/ansible/roles/nested-quota-propagation/vars/main.yml#L1)
 * running [ansible playbook `nested-quota-propagation`](https://github.com/beskar-cloud/cloud-entities/blob/main/ci/ansible/nested-quota-propagation.yml) in [CI/CD](https://github.com/beskar-cloud/cloud-entities/blob/fac938b1a7855ff45a73c12c43d9e5dd77e147ac/ci/cloud-entity-pipeline.yml#L118)

### Is it possible to define life-cycle of all personal projects?

Yes, possible and mostly automated.

Workflow of quota propagation is automated within [ansible playbook `children-project-cleanup`](https://github.com/beskar-cloud/cloud-entities/blob/main/ci/ansible/children-project-cleanup.yml).

Configuration of the feature consist of:
 * [tagging `personal-projects` umbrella project with `children-project-clean-up.*` tags](https://github.com/beskar-cloud/cloud-entities/blob/fac938b1a7855ff45a73c12c43d9e5dd77e147ac/environments/dev-beskar/openstack/projects-quotas-acls/egi_eu/personal-projects.yaml#L12-L15)
 * definition of parent project inside [`children-project-cleanup`](https://github.com/beskar-cloud/cloud-entities/blob/main/ci/ansible/roles/children-project-cleanup/vars/main.yml#L1)
 * running ansible playbook `children-project-cleanup` in [CI/CD](https://github.com/beskar-cloud/cloud-entities/blob/fac938b1a7855ff45a73c12c43d9e5dd77e147ac/ci/cloud-entity-pipeline.yml#L126)

The `children-project-cleanup` procedure defines three steps:
 * Ta] notification of the cloud user about clean-up actions (upcoming server shutoff)
 * Tb] performing server shutoff & notification of the cloud user about shutoff action done and delete actions ahead.
 * Tc] performing cloud resource deletion & notification of the cloud user about the deletion.

The notification of the cloud users is currently not done in the code as we need to answer:

* A] Do we want to notify users on personal project life-cycle steps? Alternatively we may want just to define set of rules for personal project usage (incl. life-cycle management).
* B] Getting cloud users email addresses *reliably* requires additional steps. Althogh OpenStack mapped plug-in may get the initial user's email precisely at the personal project creation. This email field (OIDC-email) is likely subject of change as time goes which leads to inaccurate email addresses stored. The most reliable user's email address is in the AAI database. There are at least two options how to get the email addresses:
  * a] cache email data and store them at infra side (we can avoid patching Keystone, we can do it in ESACO proxy)
  * b] use different channel and ask AAI (perun) for such data.


### Is it possible to define set of AppDB appliances propagated down-to personal projects?

Yes, possible, proposed below, implementation started, not finished yet.

The proposed functionality is following:
1. if umbrella parent project on top of all personal projects `personal-projects` gets specific [tag `egi.AppDB.project_nested_propagation.enable=true`] then
2. all AppDB appliances registered for umbrella `personal-projects` project are copied to all personal projects below

At this moment it is unclear whether AppDB and/or cloudkeeper has long future.
So far we implemented in [k8s cloudkeeper reloader](https://github.com/beskar-cloud/custom-helm-charts/blob/4112c3dcceb60cd8be438516d5b7665d6e213f96/egi-appliances/values.yaml#L74) so this propagation is possible.

The questions to be clarified:
* What is the cloudkeeper / AppDB future, is it worth to finish this appliances propagation still with cloudkeeper?


### As a manager of personal projects, I'm having troubles to switch between them as Horizon shows first 30 only.

Reconfigure OpenStack Horizon's local_settings to ['DROPDOWN_MAX_ITEMS=300'](https://docs.openstack.org/horizon/latest/configuration/settings.html#dropdown-max-items).



