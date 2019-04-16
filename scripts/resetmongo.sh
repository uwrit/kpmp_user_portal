#!/bin/bash
# Resets the docker image for KPMP User Mongo
docker rm kpmp-user-mongo
docker rmi kpmp-user-portal_mongodb
docker volume rm kpmp-user-portal_kpmp-mongo-data