# Railway Deployment

This package builds a single Frappe v15 image that includes:

- `frappe`
- `erpnext`
- `retail_shop`

It is prepared for a Railway deployment with **one consolidated app service**
(web + realtime + background workers + scheduler + nginx, all in one
container), plus separate `mariadb` and `redis` services.

## Why One Consolidated Service

Railway does not support attaching the same volume to multiple services (and
never plans to). The standard Frappe multi-container layout — separate
`backend`, `websocket`, `worker`, `scheduler`, and `frontend` services all
sharing one `sites` volume — is not possible there: `bench worker`,
`bench schedule`, and nginx's static asset serving all need real read/write
access to the same site files, not just the same database. Running every
process inside one container means they share a filesystem naturally, so
only one volume is needed.

## What This Uses

- Official Frappe build images: `frappe/build:version-15`, `frappe/base:version-15`
- MariaDB 10.6 as the database
- Redis 7 as cache/queue/socketio backend
- One volume mounted into the app service at `/home/frappe/frappe-bench/sites`

## Important Constraints

- This setup is prepared for the `retail_shop` app and a `frappe + erpnext + retail_shop` site.
- It does **not** include `hrms` or `hijira_payroll`.
- If you want to restore `erp.localhost`, extend `apps.json` first and rebuild the image.
- Railway free credits are usually not enough for long-running ERPNext production usage.
- All Frappe processes share one container, so a crash in any one of them
  (gunicorn, socketio, worker, scheduler, nginx) restarts the whole service.
  For a small/solo deployment this tradeoff is worth the simplicity; it is
  not a substitute for a real multi-node production setup.

## Railway Services

Create these 3 services inside one Railway project.

### 1. `mariadb`

Deploy a Docker image service:

- Image: `mariadb:10.6`
- Volume mount: `/var/lib/mysql`
- Health Check Path: leave empty (MariaDB is not HTTP)

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
- Health Check Path: leave empty (Redis is not HTTP)

### 3. `app`

Deploy this repository with **Root Directory** set to:

```text
deployment/railway
```

Railway should detect the Dockerfile automatically (Builder: Dockerfile).

- Start command: leave as the image default (`railway-start.sh`), or set it
  explicitly under Settings → Deploy → Custom Start Command.
- Volume: attach one volume at `/home/frappe/frappe-bench/sites`.
- Health Check Path: leave empty at first (see note below).
- Networking: this is the only service that needs a public domain — generate
  one under Settings → Networking.

Environment variables:

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
AUTO_MIGRATE=1
ADMIN_PASSWORD=<administrator-password>
SOCKETIO_PORT=9000
BACKGROUND_WORKERS=1
FRAPPE_SITE_NAME_HEADER=<same-as-SITE_NAME>
```

Notes:

- Set `SITE_NAME` to the actual site name you want Frappe to create.
- If you later add a custom domain, keep `SITE_NAME` aligned with the domain when possible.
- `BACKGROUND_WORKERS` controls how many worker processes `bench worker-pool`
  spawns inside the container.
- `FRAPPE_SITE_NAME_HEADER` must match `SITE_NAME` — without it, nginx falls
  back to the incoming `Host` header to pick the site, which only works once
  your public domain matches `SITE_NAME` exactly. Leaving it unset means the
  default Railway `*.up.railway.app` domain will not resolve to your site
  until a matching custom domain is attached.
- `BACKEND` and `SOCKETIO` do not need to be set — they default to
  `127.0.0.1:8000` / `127.0.0.1:9000` inside `railway-start.sh` since nginx
  proxies to the other processes in the same container.

## Suggested Deploy Order

1. Create `mariadb`, wait until healthy.
2. Create `redis`, wait until healthy.
3. Create `app` with the variables above, deploy, and watch its logs — first
   boot creates the site and installs `erpnext` + `retail_shop`, which takes
   several minutes.
4. Once `app` logs show Gunicorn, socketio, the worker pool, the scheduler,
   and nginx all started cleanly, generate a public domain on `app`.

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
- starts the consolidated `app` container (web + realtime + worker +
  scheduler + nginx)
- creates the site automatically
- exposes the app on `http://127.0.0.1:8080`

What should pass:

- `http://127.0.0.1:8080/api/method/ping` returns `{"message":"pong"}`
- the login page loads in the browser

Useful log command:

```bash
docker logs -f retail-railway-local-app
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

After the `app` service is healthy, restore the backup into the created site.

Example local backup command:

```bash
bench --site retail.localhost backup --with-files
```

Then use a one-off shell in the `app` service to run a restore.

Typical sequence inside the running `app` container:

```bash
bench --site <SITE_NAME> set-maintenance-mode on
bench --site <SITE_NAME> restore /path/to/database.sql.gz --with-public-files /path/to/public-files.tar --with-private-files /path/to/private-files.tar
bench --site <SITE_NAME> migrate
bench --site <SITE_NAME> set-maintenance-mode off
```

You will need to upload the backup files into the `sites` volume before restoring them.

## Updating The Custom App

The image clones `retail_shop` from GitHub during Docker build. The
`bench init` layer is cached (apps.json rarely changes), so a later layer
re-installs `retail_shop` on every commit using `RAILWAY_GIT_COMMIT_SHA`
and the current GitHub `main` tip.

Push to `main` and wait for the `app` service rebuild to finish, then hard
refresh the site. Startup still runs `bench migrate` when `AUTO_MIGRATE=1`.

