#!/bin/bash

#the directory where the app is deployed on the EC2 instance
cd /home/ec2-user/horizon_api_prod_001

# Activate your virtual environment, if you're using one
# source venv/bin/activate

# Install the dependencies from requirements.txt
pip3 install -r requirements.txt
