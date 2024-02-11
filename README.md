## backend-svc

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

Backend for the Analytics Service.

## Infrastructure

We use [PostgreSQL](https://www.postgresql.org/) provisioned via docker container. 
You can quickly bootstrap it for local development using contained `docker-compose.yaml`:

```bash
docker compose up backend-svc-pgdb
```

Configure if needed in `.env`.

Furthermore, in case you want an isolated launch of this service, you may utilize context-full dockerized build.
For that, simply run:

```bash
docker compose up
```