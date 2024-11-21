git config --global --unset http.sslcainfo | exit 0
git update-index --assume-unchanged .devcontainer/devcontainer.json   
# git update-index --no-assume-unchanged .devcontainer/devcontainer.json