#!/bin/bash
# ---- Start docker service
sudo service docker start

# ---- Allow ubuntu user to manage Docker service
sudo usermod -a -G docker ubuntu

# Install GitHub Actions Runner
# Need to run these commands as the ubuntu user for correct permissions
sudo -u ubuntu mkdir /home/ubuntu/actions-runner
cd /home/ubuntu/actions-runner
sudo -u ubuntu curl -o actions-runner-linux-x64-2.307.1.tar.gz -L https://github.com/actions/runner/releases/download/v2.307.1/actions-runner-linux-x64-2.307.1.tar.gz
sudo -u ubuntu tar xzf ./actions-runner-linux-x64-2.307.1.tar.gz
sudo -u ubuntu ./config.sh --url https://github.com/no10ds --token "${runner-registration-token}" --name Data-F1-Pipeline-Runner --unattended --replace

# Run the GitHub Actions Runner
sudo -u ubuntu ./run.sh &

# # Configure the GitHub Actions Runner to start on reboot
sudo crontab -l -u ubuntu | echo "@reboot sudo -u ubuntu /home/ubuntu/actions-runner/run.sh &" | sudo crontab -u ubuntu -
