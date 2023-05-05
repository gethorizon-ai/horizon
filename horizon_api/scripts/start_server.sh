#!/bin/bash

#the directory where the app is deployed on the EC2 instance
cd /home/ec2-user/horizon_api_prod_001

# Activate your virtual environment, if you're using one
# source venv/bin/activate

# Start the Flask server in the background
export FLASK_APP=main
export FLASK_ENV=production
nohup flask run --host=0.0.0.0 > /dev/null 2>&1 &
