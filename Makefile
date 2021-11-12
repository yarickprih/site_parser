ifneq (,$(wildcard ./.env))
    include .env
    export
endif


docker-up:
	sudo docker-compose up -d --build --remove-orphans
	sudo docker-compose logs -f

docker-down:
	sudo docker-compose down --remove-orphans

docker-reload:
	sudo docker-compose down --remove-orphans
	sudo docker-compose up -d --build --remove-orphans
	sudo docker-compose logs -f

docker-logs:
	sudo docker-compose logs -f

web-shell:
	sudo docker-compose exec web /bin/bash

db-shell:
	sudo docker-compose exec $(POSTGRES_HOST) psql --username=$(POSTGRES_USER) --dbname=$(POSTGRES_DB)

remove-dangling:
	sudo docker rmi $(docker images -f "dangling=true" -q)