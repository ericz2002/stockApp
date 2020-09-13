#!/bin/bash

function sigfunc() {
	popd 2>/dev/null
}

set -o nounset                              # Treat unset variables as an error
set -e

if [ ! -e env.conf ]; then
    echo "env.conf not exists in directory ${PWD}"
    echo "export env jwt_key and finnhub_token before running this script"
    exit 1
else
    source env.conf
fi

if [ ${jwt_key:-x} == "x" ]; then
    echo "secret jwt_key needs to be passed in as env var"
    exit 1
fi

if [ ${finnhub_token:-x} == "x" ]; then
    echo "finnhub_token needs to be passed in as env var"
    exit 1
fi

if [ ${mysql_username:-x} == "x" ]; then
    echo "mysql_username needs to be passed in as env var"
    exit 1
fi

if [ ${mysql_password:-x} == "x" ]; then
    echo "mysql_password needs to be passed in as env var"
    exit 1
fi

# does mysql have running instance
mysqlIns=$(docker ps -f "publish=3306" --format "{{.ID}}" | wc -l)

# start mysql if not started already
if (( mysqlIns == 0 )); then
    echo "starting mysql docker container"
    mkdir -p ~/mysql-data
    docker run -d --rm -p 3306:3306 --name=mysql \
	       -e MYSQL_DATABASE=eclass -e MYSQL_USER=stock \
	       -e MYSQL_PASSWORD=stock -e MYSQL_ROOT_PASSWORD=stock \
	       -v ~/mysql-data:/var/lib/mysql \
	       mysql
else
    echo "mysql docker container is already running"
fi

if [ "${VIRTUAL_ENV:-none}" == "none" ]; then
	echo "activate python virtual environment"
	source ./py36-venv/bin/activate
fi

pushd app
trap sigfunc TERM INT SIGUSR1
./wait-for-db.sh
