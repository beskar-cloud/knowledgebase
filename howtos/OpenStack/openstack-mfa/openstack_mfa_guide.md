#### OpenStack MFA Configuration Guide

**Introduction**

This guide will walk you through the process of enabling Multi-Factor Authentication (MFA) for OpenStack, enhancing the security of your environment. MFA is crucial for protecting sensitive resources, as it requires users to provide two or more forms of verification before accessing the system. In this setup, we will implement TOTP (Time-based One-Time Password), a widely-used MFA method that generates a unique code every 30 seconds, ensuring that even if a password is compromised, unauthorized access is prevented.

We will begin by configuring both the Keystone identity service and the Horizon dashboard to support MFA. After that, we'll create a dedicated test user and apply the MFA settings, ensuring that this user must authenticate using both a password and a TOTP code. Next, we'll generate and register a TOTP secret, create a QR code for easy setup with an authenticator app, and finally, test the entire configuration by logging in with the TOTP method. By the end of this guide, you will have a fully operational MFA setup in OpenStack, providing robust security for your cloud environment.

## Official Documentation

- [Configuring TOTP in Keystone](https://docs.openstack.org/keystone/pike/advanced-topics/auth-totp.html)

- [Time-based one-time password(TOTP) authentication support for Horizon](https://www.openstack.org/blog/new-in-openstack-bobcat-horizon-team-introduces-time-based-one-time-password-totp-authentication-support/)

### 1. Configure Keystone and Horizon

**KEYSTONE:**
Adjust your Keystone server's keystone.conf:

```
[auth]
methods = external,password,token,oauth1,totp,application_credential
```

**Restart the service after the changes**

This configuration enables TOTP (Time-based One-Time Password) as an authentication method in Keystone. The other methods listed are also supported, ensuring flexibility in how users can authenticate.


**HORIZON:**
To enable TOTP in Horizon, first set the following in the local_settings.py file:

```
OPENSTACK_KEYSTONE_MFA_TOTP_ENABLED = True

AUTHENTICATION_PLUGINS = [
  'openstack_auth.plugin.totp.TotpPlugin',
  'openstack_auth.plugin.password.PasswordPlugin',
  'openstack_auth.plugin.token.TokenPlugin'
]
```

This step ensures that Horizon (the OpenStack dashboard) is aware of and can use TOTP as an MFA method. The listed plugins define the different authentication methods that Horizon supports.

How? -> add in openstack-helm/horizon/values.yaml

```
    local_settings:
      config:
        openstack_keystone_mfa_totp_enabled: "True"
        authentication_plugins: |
          [
              'openstack_auth.plugin.totp.TotpPlugin',
              'openstack_auth.plugin.password.PasswordPlugin',
              'openstack_auth.plugin.token.TokenPlugin'
          ]

      template: |
        OPENSTACK_KEYSTONE_MFA_TOTP_ENABLED = {{ .Values.conf.horizon.local_settings.config.openstack_keystone_mfa_totp_enabled }}
        AUTHENTICATION_PLUGINS = {{ .Values.conf.horizon.local_settings.config.authentication_plugins }}
```


### 2. Create a test user

```
openstack user create mfa-user; \
openstack user set --password '5f8DE1WiaEYcTtqKEIn5' mfa-user; \
openstack project create mfa-project; \
openstack role add --user mfa-user --project mfa-project member
```
(password here is just an example)


**-> Store the returned user id for later:**

`export USER_ID=43716137b8414587a34523c5f5b3383c`
(id here is just an example)


### 3. Configure MFA for user (as admin)

Activate MFA for a specific user
```
export AUTH_TOKEN=$(openstack token issue -f value -c id)
curl -X PATCH \
-H "X-Auth-Token: $AUTH_TOKEN" \
-H "Content-Type: application/json" \
$OS_AUTH_URL/users/$USER_ID \
-d '{ "user": { "options": { "multi_factor_auth_enabled": true, "multi_factor_auth_rules": [ ["password", "totp"] ] } } }'
```
This step enables MFA for the mfa-user and specifies that both a password and a TOTP code are required for authentication. The multi_factor_auth_rules field defines the combination of methods needed.


**-> Next Step:** Confirm that MFA is enabled by checking the user's details

`openstack user show $USER_ID`


### 4. Configure TOTP (as admin)

Generate a secret.
Please replace the message string in the following example by something secure and random:

`export SECRET=$(echo -n 1937587123749071 | base32 | tr -d =)`
`echo $SECRET`

The secret is a base32-encoded string that will be used to generate TOTP codes. Replace the example string with a secure, random value.



**->** Now Register the secret in Keystone for that user, use the USER_ID from above:

```
export AUTH_TOKEN=$(openstack token issue -f value -c id)
export USER_ID=43716137b8414587a34523c5f5b3383c
curl -X POST \
-H "X-Auth-Token: $AUTH_TOKEN" \
-H "Content-Type: application/json" \
$OS_AUTH_URL/credentials \
-d '{ "credential": { "blob": "'$SECRET'", "type": "totp", "user_id": "'$USER_ID'" } }'
```

This step stores the generated TOTP secret in Keystone, associating it with the mfa-user. This allows the TOTP codes generated by the secret to be used for authentication.


### 5. Generate QR code from secret for user (as admin)
Insert the SECRET from above, adjust name / issuer, and execute the script with Python (make sure python3-qrcode package is installed):

```
#!/usr/bin/env python3
import qrcode

secret='GE4TGNZVHA3TCMRTG42DSMBXGE'
uri = 'otpauth://totp/{name}?secret={secret}&issuer={issuer}'.format(
    name='mfa-user@openstack.org',
    secret=secret,
    issuer='Keystone')

img = qrcode.make(uri)
img.save('totp.png')
```

Transfer the resulting totp.png image to the user and have them register with the **Google Authenticator OR FreeOTP+ App** by scanning the image.

This script generates a QR code containing the TOTP URI, which can be scanned by an authenticator app (like Google Authenticator or FreeOTP+). This simplifies the setup process for the user by eliminating the need to manually enter the secret.


### 6. Authenticate with TOTP (as user)
The following scripts and instructions are relevant to the user who aims to authenticate with MFA.

**6.1 TOTP MFA Script**

Create mfa-auth.sh:
```
#!/bin/bash

# Note: you can skip defining the variables here if the user
# sources their "openrc" file beforehand anyway!
OS_AUTH_URL=http://controller:5000/v3
OS_USERNAME=mfa-user
OS_USER_DOMAIN_NAME=Default
OS_PROJECT_DOMAIN_NAME=Default
OS_PROJECT_NAME=mfa-project

echo "Please enter your OpenStack Password for project $OS_PROJECT_NAME as user $OS_USERNAME: "
read -sr OS_PASSWORD

echo "Please generate and enter a TOTP authentication code: "
read -r OS_TOTP_CODE

OS_TOKEN=$(curl -v -s -X POST \
"$OS_AUTH_URL/auth/tokens?nocatalog" -H "Content-Type: application/json" \
-d '{
    "auth": {
        "identity": {
            "methods": ["password", "totp"],
            "password": {
                "user": {
                    "domain": {
                        "name": "'"$OS_USER_DOMAIN_NAME"'"
                    },
                    "name": "'"$OS_USERNAME"'",
                    "password": "'"$OS_PASSWORD"'"
                }
            },
            "totp": {
                "user": {
                    "domain": {
                        "name": "'"$OS_USER_DOMAIN_NAME"'"
                    },
                    "name": "'"$OS_USERNAME"'",
                    "passcode": "'"$OS_TOTP_CODE"'"
                }
            }
        },
        "scope": {
            "project": {
                "domain": {
                    "name": "'"$OS_PROJECT_DOMAIN_NAME"'"
                },
                "name": "'"$OS_PROJECT_NAME"'"
                }
            }
        }
    }' \
--stderr - | grep -i "X-Subject-Token" | cut -d':' -f2 | tr -d ' ' | tr -d '\r')
echo "Retrieved token: $OS_TOKEN"
```

This script interacts with OpenStack's authentication endpoint to obtain a token using both password and TOTP (Time-based One-Time Password) authentication methods.

Print Token: The echo "Retrieved token: $OS_TOKEN" command displays the retrieved token in the terminal. This allows the user to verify that the token has been successfully obtained.


**Manually Export Token:**
`export OS_TOKEN=`


### 6.2 RC File

Create mfa-user.openrc:

```
# unset any OS_ variables that conflict with token-token authentication
unset OS_USERNAME
unset OS_USER_DOMAIN_NAME
unset OS_REGION_NAME
unset OS_INTERFACE
unset OS_PASSWORD

# variables which are mandatory for the token-only authentication are:
# - OS_TOKEN
# - OS_PROJECT_NAME
# - OS_PROJECT_DOMAIN_NAME
# - OS_AUTH_URL
# (those variables should still be exported from the previous scripts and RC file)
export OS_INTERFACE=public
export OS_AUTH_TYPE=token
```

This script will make sure that all OS_ variables are aligned in a way that appeases the openstack client so that the usage of OS_TOKEN as the sole authentication for issuing commands becomes possible after acquiring said OS_TOKEN using the MFA process.

NOTE: the exact constellation of the OS_ variables is absolutely important. Having extraneous or missing variables can make the openstack client trip up easily with non-obvious error patterns!
