Create swarm init

docker info | grep -q "Swarm: active" || docker swarm init --advertise-addr 0.0.0.0

run swarm
docker stack deploy -c docker-stack.yml resumeapp --with-registry-auth

delete swarm
docker stack rm resumeapp

ip addr:
ipconfig getifaddr en0

don't forget open ports and add .env file


for local dev

docker swarm init

docker stack deploy -c docker-stack.yml resumeapp

down stack
docker stack rm resumeapp