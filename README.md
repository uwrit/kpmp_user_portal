# kpmp-user-portal
Centralized User Portal API for the KPMP app suite


## Deployment Environment
#### Mongo Variables
- `MONGO_ROOT_USERNAME` = MongoDB root username
- `MONGO_ROOT_PASSWORD` = MongoDB root user password

#### Flask Variables
- `DB` = MongoDB connection string
- `SECRET_KEY` = random alphanumeric secret for flask-admin to manage the session, a uuid will do.
- `ENV` = `development` | `production`
