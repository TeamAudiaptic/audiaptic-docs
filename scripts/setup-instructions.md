# DAVHI Setup

Follow these instructions to set up DAVHI development environment


## Setup Steps

1. `wsl --update`
2. `wsl --install --name my_wsl_name`
3. Optional: `wsl --set-default -s my_wsl_name` (in windows terminal)
4. Launch wsl
5. `cd ~`
6. Download `setup.sh` and `setup2.sh` from this folder \
    A. `wget https://raw.githubusercontent.com/TeamAudiaptic/audiaptic-docs/scripts/setup.sh` \
    B. `wget https://raw.githubusercontent.com/TeamAudiaptic/audiaptic-docs/scripts/setup2.sh`
7. `sudo chmod +x setup.sh`
8. `sudo ./setup.sh` (this may take a while)
9.  `code .` (and wait for WSL to connect)
10. `./setup2.sh`
    A. Add printed public SSH key to github, then press enter


## Optional: connect Docker Desktop to WSL

In Docker Desktop:
- Settings > Resources > WSL Integration
- Toggle this WSL distro ON
- Click 'Apply & restart'
