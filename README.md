# kpmp-user-portal
Centralized User Portal API for the KPMP app suite


## Deployment Environment
#### Mongo Variables
- `MONGO_ROOT_USERNAME` = MongoDB root username
- `MONGO_ROOT_PASSWORD` = MongoDB root user password

#### Flask Variables
In development, set these environment variables in your .env or .docker.env files:
- `DB` = MongoDB connection string
- `SECRET_KEY` = random alphanumeric secret for flask-admin to manage the session, a uuid will do.
- `ENV` = `development` | `production`
- Optional: `FLASK_RUNNING_IN_DOCKER` = `true` | `false`
In production, create a `config.py` file in `modules/config` with the following variables:
- `ENV` = `production`
- `MONGO_URI` = MongoDB connection string
- `SECRET_KEY` = random alphanumeric secret for flask-admin to manage the session, a uuid will do.
