pip install -r ./.devcontainer/requirements.txt
pip install -r ./requirements.txt

curl https://pyenv.run | bash

echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc

apt-get update
apt-get -y install gh
apt install -y jq

gh auth login

make python-setup
make api/setup

pip install -r ./sdk/requirements.txt

curl https://raw.githubusercontent.com/creationix/nvm/master/install.sh | bash

make node-setup
make ui/setup