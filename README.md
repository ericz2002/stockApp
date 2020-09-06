# stockApp

## Introduction 
This is a stock trading simulator targeted for k1-12 economy/financial education purpose.  A school teacher can setup classes, add student to classes, "digitally"fund classes or individual students, track student performance. Students will use the "digital" fund for stock transactions.

![students_assets](https://github.com/ericz2002/stockApp/blob/master/images/student_assets.png?raw=true)

## Installation

### For Development on Linux or Macos
For development purpose, follow the following steps,

#### Setup python3 virtual enviroment
```
python3 -m venv py36-venv
source py36-venv/bin/activate
```

#### Setup node
```
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.35.3/install.sh | bash
export NVM_DIR="$([ -z "${XDG_CONFIG_HOME-}" ] && printf %s "${HOME}/.nvm" || printf %s "${XDG_CONFIG_HOME}/nvm")"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
echo "install node"
nvm install v12.18.3 && nvm use v12.18.3
```

#### Clone the repo
To make contribution, you will need to fork the repo first. Follow the [fork instruction](https://docs.github.com/en/github/getting-started-with-github/fork-a-repo).

Once you have it forked, `git clone <your_fork_url> stockApp && cd stockApp`

#### Setup secret enviroment variables
```cat > env.conf <<EOF
# jwt token encryption key
export jwt_key=<key>

# finnhub access token
export finnhub_token=<token>

# mysql access credential 
export mysql_username=<username>
export mysql_password=<password>
EOF
```

#### Start the mysql database and python API on your computer
`./start_on_mac.sh`

#### Verify the python API works
In your browser, navigate to http://127.0.0.1:8000/docs. You should be able to see the FastAPI.

#### Start the Angular front end
`cd front-end && ng serve`

Once the angular build is complete, point your browser to http://127.0.0.1:4200/

### For AWS
For production deployment in AWS, login to a AWS running instance,
```
git clone <git url> stockApp && cd stockApp
./node-install.sh

export jwt_key=<key>
export finnhub_token=<token>
export mysql_username=<username>
export mysql_password=<password>

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
```

For better security practice, secret vault should be used on AWS for secret protection. For example, we used jenkins for automatic deployment on AWS when there is a push on github. The jenkins server uses secret store for password protection. When the jenkins auto deployment is triggered, it retrieves the secrets and passes them in as enviroment varibles. 

## Acknowledgment
This open source project is initially started by Eric Zhang, a NCSSM high school
student, for two folds of purpose
- computer class side: learn how to build open source projects
- economy class side: help out teachers with a free managable stock trade site

Contributors from all levels are welcome to this project.
