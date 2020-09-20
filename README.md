# stockApp

## Introduction 
This is a stock trading simulator targeted for k1-12 economy/financial education purpose.  A school teacher can setup classes, add student to classes, "digitally"fund classes or individual students, track student performance. Students will use the "digital" fund for stock transactions.

![students_assets](https://github.com/ericz2002/stockApp/blob/master/images/student_assets.png?raw=true)

## Installation

### For Development on Linux or Macos
For development purpose, follow the following steps,

#### Setup node
```
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.35.3/install.sh | bash
export NVM_DIR="$([ -z "${XDG_CONFIG_HOME-}" ] && printf %s "${HOME}/.nvm" || printf %s "${XDG_CONFIG_HOME}/nvm")"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
echo "install node"
nvm install v12.18.3 && nvm use v12.18.3
npm install -g @angular/cli
```

#### Clone the repo
To make contribution, you will need to fork the repo first. Follow the [fork instruction](https://docs.github.com/en/github/getting-started-with-github/fork-a-repo).

Once you have it forked, `git clone <your_fork_url> stockApp && cd stockApp`

#### Setup python3 virtual enviroment
For ubuntu, the following is necessary:
```
apt-get update -y
sudo apt-get install -y python3-venv
```

The following is common for ubuntu and centos:
```
python3 -m venv py36-venv
source py36-venv/bin/activate
pip install -r requirements.txt
```


#### Setup secret enviroment variables
```
cat > env.conf <<EOF
# jwt token encryption key
export jwt_key=<key>

# finnhub access token
export finnhub_token=<token>

# mysql access credential 
export mysql_username=<username>
export mysql_password=<password>
EOF
```

#### Ubuntu docker install
```
sudo apt update
sudo apt install apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu bionic stable"
sudo apt update
apt-cache policy docker-ce
sudo apt install docker-ce
```

#### Windows 10 docker install 
For Windows 10, hyper-v should be enabled first. User may need to adjust BIOS setting first in order to 
enable hyper v. For example, in Lenova laptop BIOS setting, under Security tab, intel virtualization 
technology should be enabled. 

After hyper-v is enabled, windows 10 docker desktop can be installed. This is the docker daemon for 
Windows 10 enviroment. One should follow [this instruction](https://nickjanetakis.com/blog/setting-up-docker-for-windows-and-wsl-to-work-flawlessly) to set up the daemon.

To connect to the Windows 10 docker daemon, in WSL,
`echo "export DOCKER_HOST=tcp://localhost:2375" >> ~/.bashrc && source ~/.bashrc`

#### Start the mysql database and python API on your computer
`./start_on_mac.sh`

#### Verify the python API works
In your browser, navigate to http://127.0.0.1:8000/docs. You should be able to see the FastAPI.

#### Start the Angular front end
`cd front-end && ng serve`

Once the angular build is complete, point your browser to http://127.0.0.1:4200/

### Auto deployment on AWS
Auto deployment means when a change is committed and pushed into this repo, the updated code is automatically deployed in the production enviroment. 
[Jenkins](https://www.jenkins.io/doc/) can be used to assist the auto deployment. Here is an example on how to use Jenkins for auto deployment 
in AWS. Firt, install Jenkins on a AWS instance. This can be done via linux package manager. Alternatively, Jenkins docker image works too. 
After Jenkins is installed and started, do the following one-time setup on the AWS instance,
```
git clone https://github.com/ericz2002/stockApp.git stockApp && cd stockApp
./node-install.sh
```

Once the one-time setup is done, setup a Jenkins freedom pipeline with the following script

set -o nounset
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
	       -e MYSQL_DATABASE=eclass -e MYSQL_USER=${mysql_username} \
	       -e MYSQL_PASSWORD=${mysql_password} -e MYSQL_ROOT_PASSWORD=${mysql_password} \
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
docker run -d --rm --name stockapi --net host \
           -e jwt_key=${jwt_key} -e finnhub_token=${finnhub_token} \
           -e mysql_username=${mysql_username} -e mysql_password=${mysql_password} \
	   stockapi 

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

For better security practice, the jenkins server secret store is used for password protection. When the jenkins auto deployment is triggered, it retrieves the secrets and passes them into the above bash script as enviroment varibles. 

To trigger the auto deploment, this repo has a webhook pointing to the AWS Jenkins URL. A push to this repo will trigger the webhook and send notification to the Jenkins which will kick off the above script for auto deployment.

## Acknowledgment
This open source project is initially started by Eric Zhang, a NCSSM high school
student, for two folds of purpose
- computer class side: learn how to build open source projects
- economy class side: help out teachers with a free managable stock trade site

Contributors from all levels are welcome to this project.
