#!/bin/bash
#===============================================================================
#
#          FILE: wait-for-db.sh
# 
#         USAGE: ./wait-for-db.sh 
#===============================================================================

set -o nounset                              # Treat unset variables as an error
set -e

while true; do
	state=$(python test_port.py)
	if [ "${state}" == "open" ]; then
		echo "db port open, starting api service"
		break
	else
		echo "db port not open, sleep 5 second and try again"
		sleep 5
	fi
done

python main.py 
