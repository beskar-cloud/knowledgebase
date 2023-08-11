# How to fix not functional OpenStack volume detach

## Problem
In OpenStack Yoga just upgraded from Wallaby.
Every volume detach operation fails down in keystone on KeyError exception. Consequently cinder-api gets HTTP response 500. Volume entity ends in `detaching` state.

```log
2023-07-28 15:10:15.471188 2023-07-28 15:10:15.471 11 DEBUG keystone.server.flask.request_processing.middleware.auth_context [req-60b0c93f-0d81-4067-9500-0a9a411306a6 bc28a25a7...0d4858be0c191 7587d8...5976007 - f4614....017c89d96880 f4614....017c89d96880] RBAC: auth_context: {'token': <TokenModel (audit_id=OS6v..........lZL6Q, audit_chain_id=['OS6v..........lZL6Q']) at 0x7f6d959f0e80>, 'domain_id': None, 'trust_id': None, 'trustor_id': None, 'trustee_id': None, 'domain_name': None, 'group_ids': [], 'user_id': 'bc28a25a7...0d4858be0c191', 'user_domain_id': 'f4614....017c89d96880', 'system_scope': None, 'project_id': '7587d8...5976007', 'project_domain_id': 'f4614....017c89d96880', 'roles': ['member', 'creator', 'reader'], 'is_admin_project': True, 'service_user_id': None, 'service_user_domain_id': None, 'service_project_id': None, 'service_project_domain_id': None, 'service_roles': []} fill_context /var/lib/openstack/lib/python3.8/site-packages/keystone/server/flask/request_processing/middleware/auth_context.py:478
2023-07-28 15:10:15.626862 mod_wsgi (pid=11): Exception occurred processing WSGI script '/var/www/cgi-bin/keystone/keystone-wsgi-public'.
2023-07-28 15:10:15.627348 Traceback (most recent call last):
2023-07-28 15:10:15.627474   File "/var/lib/openstack/lib/python3.8/site-packages/flask/app.py", line 2091, in __call__
2023-07-28 15:10:15.627492     return self.wsgi_app(environ, start_response)
2023-07-28 15:10:15.627499   File "/var/lib/openstack/lib/python3.8/site-packages/werkzeug/middleware/proxy_fix.py", line 187, in __call__
2023-07-28 15:10:15.627501     return self.app(environ, start_response)
...
2023-07-28 15:10:15.627837   File "/var/lib/openstack/lib/python3.8/site-packages/keystone/api/auth.py", line 315, in post
2023-07-28 15:10:15.627839     token = authentication.authenticate_for_token(auth_data)
2023-07-28 15:10:15.627844   File "/var/lib/openstack/lib/python3.8/site-packages/keystone/api/_shared/authentication.py", line 212, in authenticate_for_token
2023-07-28 15:10:15.627847     app_cred_id = token_auth['application_credential']['id']
2023-07-28 15:10:15.627858 KeyError: 'application_credential'
10.233.116.201 - - [28/Jul/2023:15:10:15 +0000] "POST /v3/auth/tokens HTTP/1.1" 500 531 "-" "cinder-api keystoneauth1/4.5.0 python-requests/2.27.1 CPython/3.8.10"

```
Fron the above keystone log snippet is clear that users' identity is sent to keystone instead of (nova eventually cinder) identity of service user.


## Resolution

There was recent change of the OpenStack community as an reaction on [CVE-2023-2088](https://nvd.nist.gov/vuln/detail/CVE-2023-2088) vulneability. [CVE-2023-2088](https://nvd.nist.gov/vuln/detail/CVE-2023-2088) mitigation relies on specific nova and cinder reconfiguration the way that OpenStack services (nova and cinder) use service user tokens with short TTL instead of service user credentials.
In order to implement such change [follow this guide](https://docs.openstack.org/cinder/latest/configuration/block-storage/service-token.html).


## References
* https://docs.openstack.org/cinder/latest/configuration/block-storage/service-token.html
* https://bugs.launchpad.net/cinder/+bug/2004555
* https://docs.openstack.org/releasenotes/cinder/yoga.html#upgrade-notes
