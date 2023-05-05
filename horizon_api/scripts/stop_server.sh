#!/bin/bash

#the directory where the app is deployed on the EC2 instance
cd /home/ec2-user/horizon_api_prod_001

# Check if the server is running and stop it
if pgrep -f "flask run" > /dev/null
then
    pkill -f "flask run"
fi
