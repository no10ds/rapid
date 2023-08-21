#!/usr/bin/env bash

# Enable SSM
sudo snap install amazon-ssm-agent --classic
sudo snap start amazon-ssm-agent

# Update base packages
sudo apt update -y
sudo dpkg --configure -a

# Install make
sudo apt-get -y install make

# Install Java
sudo apt-get install default-jre -y

# Install jq
sudo apt-get install jq -y

# Install Docker
sudo apt-get install docker.io -y

# Install zip
sudo apt-get install zip -y

# Install unzip
sudo apt-get install unzip -y

# Install GitHub cli (gh)
type -p curl >/dev/null || sudo apt install curl -y
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh -y

# Install V2 AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

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
