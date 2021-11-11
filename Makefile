export:
	export FLASK_APP=main.py


docker-up:
	sudo docker-compose up -d --build --remove-orphans && sudo docker-compose logs -f