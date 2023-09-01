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
