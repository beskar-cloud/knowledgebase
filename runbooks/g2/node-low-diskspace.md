# Node not enough of free disk space

**Initial runbook version.**

## Problem

Node available diskspace running low.

## Analysis
 * identify what files are taking so much time on reported mounted directory (`du`, `ncdu`)
 * identify componnet responsible for discovered huge files

## Resolution
 * reconfigure component to avoid such problems (deletion of rotated files)

## References
 * 
