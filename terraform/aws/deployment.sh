#!/bin/bash

# install and configure docker on the ec2 instance
sudo yum update -y
sudo amazon-linux-extras install docker -y
sudo service docker start
sudo systemctl enable docker

# create a dockerfile

# build the docker image
#sudo docker build -t <image-tag> 
# sudo docker build -t mlops-project-api .

# login to your docker hub account
#cat ~/my_password.txt | sudo docker login --username <your-docker-id> --password-stdin
# cat ~/docker_password.txt | sudo docker login --username ar3ee3arcs --password-stdin

# use the docker tag command to give the image a new name
#sudo docker tag <image-tag> <repository-name>
# sudo docker tag mlops-project-api ar3ee3arcs/learn-mlopsz:dev

# push the image to your docker hub repository
#sudo docker push <repository-name>
# sudo docker push ar3ee3arcs/learn-mlopsz:dev

# start the container to test the image
#sudo docker run -dp 80:80 <repository-name> 
sudo docker run -dp 80:80 --env-file .env ar3ee3arcs/learn-mlopsz:dev