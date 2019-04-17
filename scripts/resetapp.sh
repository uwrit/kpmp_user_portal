#!/bin/bash
# Resets the docker image for KPMP User App
docker rm kpmp-user-app
docker rmi kpmp-user-portal_app
