# DAVHI Setup

Follow these instructions to set up DAVHI development environment


## Setup Steps

1. `wsl --update`
2. `wsl --install --name my_wsl_name`
3. Optional: `wsl --set-default -s my_wsl_name`
4. Launch wsl
5. Download `setup.sh` and `setup2.sh` from this folder \
    A. `wget https://raw.githubusercontent.com/TeamAudiaptic/audiaptic-docs/scripts/setup.sh` \
    B. `wget https://raw.githubusercontent.com/TeamAudiaptic/audiaptic-docs/scripts/setup2.sh`
6. `sudo chmod +x setup.sh`
7. `sudo ./setup.sh` (this may take a while)
8. `code .`
9. `./setup2.sh`
    A. Add printed public SSH key to github, then press enter


## Optional: connect Docker Desktop to WSL

In Docker Desktop:
- Settings > Resources > WSL Integration
- Toggle this WSL distro ON
- Click 'Apply & restart'
