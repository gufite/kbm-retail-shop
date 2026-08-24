# Railway Deployment

This package builds a single Frappe v15 image that includes:

- `frappe`
- `erpnext`
- `retail_shop`

It is prepared for a Railway multi-service deployment, not a single-container app.

## What This Uses

- Official Frappe build images: `frappe/build:version-15`, `frappe/base:version-15`
- MariaDB 10.6 as the database
- Redis 7 as cache/queue/socketio backend
- One shared `sites` volume mounted into every Frappe service

## Important Constraints

- This setup is prepared for the `retail_shop` app and a `frappe + erpnext + retail_shop` site.
- It does **not** include `hrms` or `hijira_payroll`.
- If you want to restore `erp.localhost`, extend `apps.json` first and rebuild the image.
- Railway free credits are usually not enough for long-running ERPNext production usage.

## Railway Services

Create these services inside one Railway project.

### 1. `mariadb`

Deploy a Docker image service:

- Image: `mariadb:10.6`
- Volume mount: `/var/lib/mysql`

Environment variables:

```text
MARIADB_ROOT_PASSWORD=<strong-password>
MARIADB_ROOT_HOST=%
MARIADB_AUTO_UPGRADE=1
```

### 2. `redis`

Deploy a Docker image service:

- Image: `redis:7-alpine`
- Start command: `redis-server --appendonly yes`
- Volume mount: `/data`

### 3. Frappe services from this directory

For each service below, deploy **the same repository** and set the **Root Directory** to:

```text
deployment/railway
```

Using each service's **Volumes** tab (not a Dockerfile `VOLUME` — Railway's Dockerfile builder rejects that instruction), attach the same shared volume to every Frappe service at:

```text
/home/frappe/frappe-bench/sites
```

Create these services:

- `frontend`
- `backend`
- `websocket`
- `worker`
- `scheduler`

Recommended start commands:

```text
frontend  -> nginx-entrypoint.sh
backend   -> start.sh
websocket -> node /home/frappe/frappe-bench/apps/frappe/socketio.js
worker    -> bench worker --queue short,default,long
scheduler -> bench schedule
```

Only expose `frontend` with Railway public networking.

Frontend-specific environment variables:

```text
BACKEND=backend:8000
SOCKETIO=websocket:9000
FRAPPE_SITE_NAME_HEADER=<your-site-name>
```

Set `FRAPPE_SITE_NAME_HEADER` to the same value as `SITE_NAME`. Without it, nginx falls back to the incoming `Host` header to pick the site, which only works once your public domain matches `SITE_NAME` exactly — leaving it unset means the default Railway `*.up.railway.app` domain will not resolve to your site until a matching custom domain is attached.

## Shared Environment Variables For All Frappe Services

Set these on every Frappe service:

```text
SITE_NAME=<your-site-name>
DB_TYPE=mariadb
DB_HOST=mariadb.railway.internal
DB_PORT=3306
DB_ROOT_USER=root
DB_ROOT_PASSWORD=<same-as-mariadb-root-password>
REDIS_CACHE_HOST=redis.railway.internal
REDIS_CACHE_PORT=6379
REDIS_QUEUE_HOST=redis.railway.internal
REDIS_QUEUE_PORT=6379
REDIS_SOCKETIO_HOST=redis.railway.internal
REDIS_SOCKETIO_PORT=6379
INSTALL_APPS=erpnext,retail_shop
AUTO_SETUP_SITE=1
AUTO_MIGRATE=0
ADMIN_PASSWORD=<administrator-password>
SOCKETIO_PORT=9000
BACKGROUND_WORKERS=1
```

Notes:

- Set `SITE_NAME` to the actual site name you want Frappe to create.
- If you later add a custom domain, keep `SITE_NAME` aligned with the domain when possible.
- `AUTO_SETUP_SITE=1` allows one service to create the site under a lock on first boot.
- `AUTO_MIGRATE=0` keeps non-backend services from running repeat migrations.

Set this override only on the `backend` service:

```text
AUTO_MIGRATE=1
```

## Suggested Deploy Order

1. Create `mariadb`
2. Create `redis`
3. Create `backend`
4. Create `websocket`
5. Create `worker`
6. Create `scheduler`
7. Create `frontend`
8. Generate the public domain only on `frontend`

## Local Smoke Test

You can test the same container layout locally with plain Docker.

From the app repository root:

```bash
chmod +x deployment/railway/scripts/local-smoke-test.sh
chmod +x deployment/railway/scripts/local-smoke-test-down.sh
./deployment/railway/scripts/local-smoke-test.sh
```

What it does:

- builds the Railway image locally
- starts MariaDB and Redis
- starts `backend`, `websocket`, `worker`, `scheduler`, and `frontend`
- creates the site automatically
- exposes the frontend on `http://127.0.0.1:8080`

What should pass:

- `http://127.0.0.1:8080/api/method/ping` returns `{"message":"pong"}`
- the login page loads in the browser

Useful log commands:

```bash
docker logs -f retail-railway-local-backend
docker logs -f retail-railway-local-frontend
docker logs -f retail-railway-local-worker
```

To stop the local stack:

```bash
./deployment/railway/scripts/local-smoke-test-down.sh
```

To wipe the persisted test data too:

```bash
docker volume rm retail-railway-local-db retail-railway-local-redis retail-railway-local-sites
docker network rm retail-railway-local-net
```

## Restoring Your Existing Retail Data

This setup is meant for the simpler site:

- `retail.localhost`

After the Frappe services are healthy, restore the backup into the created site.

Example local backup command:

```bash
bench --site retail.localhost backup --with-files
```

Then use a one-off shell in the `backend` service to run a restore.

Typical sequence inside the running backend container:

```bash
bench --site <SITE_NAME> set-maintenance-mode on
bench --site <SITE_NAME> restore /path/to/database.sql.gz --with-public-files /path/to/public-files.tar --with-private-files /path/to/private-files.tar
bench --site <SITE_NAME> migrate
bench --site <SITE_NAME> set-maintenance-mode off
```

You will need to upload the backup files into the shared `sites` volume before restoring them.

## Updating The Custom App

This image builds `retail_shop` from:

```text
https://github.com/gufite/kbm-retail-shop.git
```

When you push updates to that repo, trigger a new Railway deployment for the Frappe services so the image rebuilds and then runs startup migrations.
