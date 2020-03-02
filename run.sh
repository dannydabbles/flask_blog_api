#!/bin/bash

touch dev.db
cp .env.example .env
docker-compose build
docker-compose run --rm manage db init
docker-compose run --rm manage db migrate
docker-compose run --rm manage db upgrade
docker-compose run --rm manage test
docker-compose up flask-prod
