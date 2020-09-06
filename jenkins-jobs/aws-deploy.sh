#!/usr/bin/env bash

set -o nounset                              # Treat unset variables as an error
set -e
set +x

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

mysqlIns=$(docker ps -f "publish=3306" --format "{{.ID}}" | wc -l)
# start mysql if not started already
if (( mysqlIns == 0 )); then
    echo "starting mysql docker container"
    sudo mkdir -p /var/lib/mysql
    docker run -d --rm -p 3306:3306 --name=mysql \
	       -e MYSQL_DATABASE=eclass -e MYSQL_USER=stock \
	       -e MYSQL_PASSWORD=stock -e MYSQL_ROOT_PASSWORD=stock \
	       -v /var/lib/mysql:/var/lib/mysql \
	       mysql
else
    echo "mysql docker container is already running"
fi

apiIns=$(docker ps -f "name=stockapi" --format "{{.ID}}" | wc -l)
if (( apiIns > 0 )); then
	docker stop stockapi
fi

apiImgIns=$(docker images -f "reference=stockapi" --format "{{.ID}}" | wc -l)
if (( apiImgIns > 0 )); then
	docker rmi stockapi
fi

docker build -t stockapi .
echo "starting stockapi container"
docker run -d --rm --name stockapi --net host stockapi

echo "stop nginx"
nginxIns=$(docker ps -f "name=nginx" --format "{{.ID}}" | wc -l)
if ((nginxIns > 0)); then
	docker stop nginx
fi

pushd front-end
npm install
ng build --prod --configuration production
popd
docker run -d --rm --net host --name nginx \
	-v $(pwd)/nginx/default.conf:/etc/nginx/conf.d/default.conf \
	-v $(pwd)/front-end/dist:/opt/front-end \
	-v /var/lib/sslcerts:/etc/nginx/certs:ro \
	nginx


