pip install -r ./.devcontainer/requirements.txt

make python-setup
make api/setup

make node-setup
make ui/setup