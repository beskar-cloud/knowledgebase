# Metamonitoring dead man's switch, end-to-end alerting test

## Problem

This alert should fire continuously to test monitoring and alerting infrastructure. Read more about principle from link below.

## Analysis

If you got this alert notification then alert has invalid severity or there is missing Alertmanager silence on this alert.

## Resolution

Configure Prometheus monitoring-infrastructure/dead-mans-switch.yml alerts to not fire by default to default notification channels (for instance by setting severity to `info`) and doublecheck given severity is silenced in Alertmanager.

## References
 * https://jpweber.io/blog/taking-advantage-of-deadmans-switch-in-prometheus/
