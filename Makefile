.SILENT:

ifneq (,$(wildcard ./.env))
    include .env
    export
endif


ps:
	sudo docker ps -a

images:
	sudo docker images

stop:
	sudo docker-compose stop $(service)

start:
	sudo docker-compose start $(service)

build:
	COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1 sudo docker-compose build

run: build
	sudo docker-compose up -d --remove-orphans

down:
	sudo docker-compose down --remove-orphans

reload: down build
	sudo docker-compose up -d --build --remove-orphans

logs:
	sudo docker-compose logs -f

web-shell:
	sudo docker-compose exec web /bin/bash

python-shell:
	sudo docker-compose exec web flask shell

db-shell:
	sudo docker-compose exec $(POSTGRES_HOST) psql --username=$(POSTGRES_USER) --dbname=$(POSTGRES_DB)

clean:
	sudo docker rmi $$(sudo docker images -f "dangling=true" -q)

prune-containers:
	sudo docker container prune --force

prune-images:
	sudo docker image prune --force --all

prune-volumes:
	sudo docker volume prune --force

test:
	pytest -v -s

lint:
	pre-commit run --all
