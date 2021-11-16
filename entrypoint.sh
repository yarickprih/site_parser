#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

if [ ! -d "migrations" ]
then
    echo "\nInitiating migrations setup..."
    flask db init
    echo "Migrations folder created"
fi

echo "\nRunning migrations"
flask db migrate

echo "\nRolling database migrations"
flask db upgrade

exec "$@"