# Rabbitmq Low File Descriptors

**Initial runbook version.**

## Problem

I suppose you are using Linux and many distributions set this ulimit to 1024 by default. When RabbitMQ reaches this limit, it can't accept more connections.

## Analysis
 * 

## Resolution
 * [Increase number of file descriptors](https://serverfault.com/questions/752086/how-to-permanently-increase-rabbitmq-file-descriptors-limit)

## References
 * [Rabbitmq Troubleshooting](https://www.rabbitmq.com/troubleshooting.html)
