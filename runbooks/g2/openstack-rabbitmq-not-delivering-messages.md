# Rabbitmq Returning Messages

**Initial runbook version.**

## Problem

Rabbitmq is returning messages instead of delivering them.

## Analysis
 * Check increase in the queue with `rabbitmq_queue_messages_total` metric. If the queue is full, mesage drop is expected.
 * Inspect logs on the Rabbitmq instance that is returning messages: `kubectl -n openstack logs`

## Resolution
 * [Fix the overcrowded queue](./openstack-rabbitmq-high-message-load.md)
 * Resolve the issue from logs

## References
 * [Rabbitmq Troubleshooting](https://www.rabbitmq.com/troubleshooting.html)
