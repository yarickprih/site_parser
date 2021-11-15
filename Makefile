.SILENT:

ifneq (,$(wildcard ./.env))
    include .env
    export
endif


ps:
	sudo docker ps -a

stop:
	sudo docker-compose stop $(service)

start:
	sudo docker-compose start $(service)

up:
	sudo docker-compose up -d --build --remove-orphans
	sudo docker-compose logs -f

down:
	sudo docker-compose down --remove-orphans

reload: down
	sudo docker-compose up -d --build --remove-orphans
	sudo docker-compose logs -f

logs:
	sudo docker-compose logs -f

web-shell:
	sudo docker-compose exec web /bin/bash

python-shell:
	sudo docker-compose exec web python

db-shell:
	sudo docker-compose exec $(POSTGRES_HOST) psql --username=$(POSTGRES_USER) --dbname=$(POSTGRES_DB)