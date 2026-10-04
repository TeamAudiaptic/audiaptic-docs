#!/usr/bin/env bash

# setup steps that need to be run as user

if (( $EUID == 0 )); then
    echo "Do not run as sudo or root"
    exit 1
fi

# git setup
echo "Git config..."
read -p "Git username: " username
git config --global user.name "$username"
read -p "Git email: " email
git config --global user.email "$email"
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.cm "commit -m"
git config --global alias.a "commit --amend"
git config --global alias.amend "commit --amend --no-edit"

# clone repos
echo "Cloning repos..."

mkdir -p davhi

REPOS=(
    audiaptic-server
    audiaptic-client
    audiaptic-max
    audiaptic-docs
)

for repo in "${REPOS[@]}"; do
    if [[ ! -d "davhi/$repo" ]]; then
        git clone "https://github.com/TeamAudiaptic/$repo.git" "davhi/$repo" &> $QUIET \
            && echo "Cloned $repo into ./davhi/$repo_name" \
            || echo "Error cloning $repo" >&2
    else
        echo "$repo already exists."
    fi
done

sudo chown -R $(whoami) davhi


echo "Installing vscode extensions..."

# python
code --install-extension ms-python.black-formatter
code --install-extension ms-python.python
code --install-extension kevinrose.vsc-python-indent

# markdown
code --install-extension yzhang.markdown-all-in-one
code --install-extension christian-kohler.npm-intellisense
code --install-extension unifiedjs.vscode-mdx
code --install-extension xyc.vscode-mdx-preview

# nodejs
code --install-extension esbenp.prettier-vscode
code --install-extension ritwickdey.liveserver
code --install-extension christian-kohler.npm-intellisense
code --install-extension christian-kohler.path-intellisense
code --install-extension formulahendry.code-runner
code --install-extension mikestead.dotenv
code --install-extension xabikos.JavaScriptSnippets

# rect
code --install-extension msjsdiag.vscode-react-native
code --install-extension dsznajder.es7-react-js-snippets

# docker
code --install-extension ms-azuretools.vscode-containers
code --install-extension ms-azuretools.vscode-docker


# create ssh key
echo "Creating ssh key..."
KEY_PATH="$HOME/.ssh/id_ed25519"
if [[ ! -f "$KEY_PATH" ]]; then
    ssh-keygen -t ed25519 -N "" -f "$KEY_PATH"
else
    echo "SSH key already exists at $KEY_PATH"
fi
echo
echo "Public key (add to github):"
cat "$KEY_PATH.pub"