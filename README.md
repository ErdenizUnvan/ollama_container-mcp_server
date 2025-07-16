# ollama_container-mcp_server

Install Docker, docker machine, docker compose at Ubuntu:

sudo apt update

sudo apt install -y ca-certificates curl gnupg lsb-release


sudo mkdir -p /etc/apt/keyrings

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
  sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) \
  signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update

sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

sudo docker run hello-world

sudo usermod -aG docker $USER

newgrp docker

sudo reboot

sudo apt install openssh-server

sudo apt install docker-compose -y

base=https://github.com/docker/machine/releases/download/v0.16.2 &&
  curl -L $base/docker-machine-$(uname -s)-$(uname -m) > ./docker-machine &&
  chmod +x ./docker-machine &&
  sudo mv ./docker-machine /usr/local/bin/docker-machine

Run Ollama Container at Docker:

docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama

docker exec -it ollama bash

ollama pull llama3.2

#if it is already installed:

ollama run llama3.2

exit with: Ctrl+D

exit the container: exit

learn ip address of ubuntu docker host: ip a

use the ip address for the python code of ai_agent_gradio_llama.py after http:// 

Develop MCP Server With OpenAI API

python=3.12.9

pip install -r requirements.txt

At one terminal: fastmcp dev test_tools_mcp_server.py

Open the link at webbrowser.

press connect button at webbrowser.

At another terminal: python ai_agent_gradio_llama.py



