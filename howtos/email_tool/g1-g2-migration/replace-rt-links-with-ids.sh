#!/usr/bin/env bash
# replace-rt-links-with-ids.sh <file-with-rt-links>
#
# Replaces all occurences of RT ticket URLs in a file with just ID of the tickets extracted from respective URL.
#
# Execution example:
# $ ./replace-rt-links-with-ids.sh ./projects-data/projects-data-for-mail-2.csv
#

sed -i 's/https:\/\/rt\.[^;]*id=\([0-9]\+\)/\1/g' $1
