#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE_TAG="${IMAGE_TAG:-retail-shop-railway:local}"
PROJECT_PREFIX="${PROJECT_PREFIX:-retail-railway-local}"
SITE_NAME="${SITE_NAME:-retail.local}"
DB_ROOT_PASSWORD="${DB_ROOT_PASSWORD:-retail-root-pass}"
ADMIN_PASSWORD="${ADMIN_PASSWORD:-admin}"
FRONTEND_PORT="${FRONTEND_PORT:-8080}"

NETWORK_NAME="${PROJECT_PREFIX}-net"
DB_VOLUME="${PROJECT_PREFIX}-db"
REDIS_VOLUME="${PROJECT_PREFIX}-redis"
SITES_VOLUME="${PROJECT_PREFIX}-sites"

DB_CONTAINER="${PROJECT_PREFIX}-mariadb"
REDIS_CONTAINER="${PROJECT_PREFIX}-redis"
BACKEND_CONTAINER="${PROJECT_PREFIX}-backend"
WEBSOCKET_CONTAINER="${PROJECT_PREFIX}-websocket"
WORKER_CONTAINER="${PROJECT_PREFIX}-worker"
SCHEDULER_CONTAINER="${PROJECT_PREFIX}-scheduler"
FRONTEND_CONTAINER="${PROJECT_PREFIX}-frontend"

containers=(
	"${FRONTEND_CONTAINER}"
	"${SCHEDULER_CONTAINER}"
	"${WORKER_CONTAINER}"
	"${WEBSOCKET_CONTAINER}"
	"${BACKEND_CONTAINER}"
	"${REDIS_CONTAINER}"
	"${DB_CONTAINER}"
)

cleanup_containers() {
	local name
	for name in "${containers[@]}"; do
		if docker ps -a --format '{{.Names}}' | grep -Fxq "${name}"; then
			docker rm -f "${name}" >/dev/null
		fi
	done
}

wait_for_container_state() {
	local name="$1"
	local expected="$2"
	local timeout="${3:-120}"
	local elapsed=0
	local state

	while true; do
		state="$(docker inspect -f '{{.State.Status}}' "${name}")"
		if [ "${state}" = "${expected}" ]; then
			return
		fi
		if [ "${elapsed}" -ge "${timeout}" ]; then
			echo "Timed out waiting for ${name} to reach state ${expected}. Current state: ${state}" >&2
			exit 1
		fi
		sleep 2
		elapsed=$((elapsed + 2))
	done
}

wait_for_http() {
	local url="$1"
	local timeout="${2:-300}"
	local elapsed=0

	while true; do
		if curl -fsS "${url}" >/dev/null 2>&1; then
			return
		fi
		if [ "${elapsed}" -ge "${timeout}" ]; then
			echo "Timed out waiting for HTTP endpoint ${url}" >&2
			exit 1
		fi
		sleep 5
		elapsed=$((elapsed + 5))
	done
}

common_frappe_env=(
	-e "SITE_NAME=${SITE_NAME}"
	-e "DB_TYPE=mariadb"
	-e "DB_HOST=${DB_CONTAINER}"
	-e "DB_PORT=3306"
	-e "DB_ROOT_USER=root"
	-e "DB_ROOT_PASSWORD=${DB_ROOT_PASSWORD}"
	-e "REDIS_CACHE_HOST=${REDIS_CONTAINER}"
	-e "REDIS_CACHE_PORT=6379"
	-e "REDIS_QUEUE_HOST=${REDIS_CONTAINER}"
	-e "REDIS_QUEUE_PORT=6379"
	-e "REDIS_SOCKETIO_HOST=${REDIS_CONTAINER}"
	-e "REDIS_SOCKETIO_PORT=6379"
	-e "INSTALL_APPS=erpnext,retail_shop"
	-e "AUTO_SETUP_SITE=1"
	-e "AUTO_MIGRATE=0"
	-e "ADMIN_PASSWORD=${ADMIN_PASSWORD}"
	-e "SOCKETIO_PORT=9000"
	-e "BACKGROUND_WORKERS=1"
)

echo "Building ${IMAGE_TAG} from ${ROOT_DIR} ..."
docker build -t "${IMAGE_TAG}" "${ROOT_DIR}"

echo "Resetting local smoke-test containers ..."
cleanup_containers

docker network inspect "${NETWORK_NAME}" >/dev/null 2>&1 || docker network create "${NETWORK_NAME}" >/dev/null
docker volume inspect "${DB_VOLUME}" >/dev/null 2>&1 || docker volume create "${DB_VOLUME}" >/dev/null
docker volume inspect "${REDIS_VOLUME}" >/dev/null 2>&1 || docker volume create "${REDIS_VOLUME}" >/dev/null
docker volume inspect "${SITES_VOLUME}" >/dev/null 2>&1 || docker volume create "${SITES_VOLUME}" >/dev/null

echo "Starting MariaDB and Redis ..."
docker run -d \
	--name "${DB_CONTAINER}" \
	--network "${NETWORK_NAME}" \
	-e "MARIADB_ROOT_PASSWORD=${DB_ROOT_PASSWORD}" \
	-e "MARIADB_ROOT_HOST=%" \
	-e "MARIADB_AUTO_UPGRADE=1" \
	-v "${DB_VOLUME}:/var/lib/mysql" \
	mariadb:10.6 >/dev/null

docker run -d \
	--name "${REDIS_CONTAINER}" \
	--network "${NETWORK_NAME}" \
	-v "${REDIS_VOLUME}:/data" \
	redis:7-alpine \
	redis-server --appendonly yes >/dev/null

wait_for_container_state "${DB_CONTAINER}" running 180
wait_for_container_state "${REDIS_CONTAINER}" running 60

echo "Starting Frappe services ..."
docker run -d \
	--name "${BACKEND_CONTAINER}" \
	--network "${NETWORK_NAME}" \
	-v "${SITES_VOLUME}:/home/frappe/frappe-bench/sites" \
	"${common_frappe_env[@]}" \
	-e "AUTO_MIGRATE=1" \
	"${IMAGE_TAG}" \
	start.sh >/dev/null

docker run -d \
	--name "${WEBSOCKET_CONTAINER}" \
	--network "${NETWORK_NAME}" \
	-v "${SITES_VOLUME}:/home/frappe/frappe-bench/sites" \
	"${common_frappe_env[@]}" \
	"${IMAGE_TAG}" \
	node /home/frappe/frappe-bench/apps/frappe/socketio.js >/dev/null

docker run -d \
	--name "${WORKER_CONTAINER}" \
	--network "${NETWORK_NAME}" \
	-v "${SITES_VOLUME}:/home/frappe/frappe-bench/sites" \
	"${common_frappe_env[@]}" \
	"${IMAGE_TAG}" \
	bench worker --queue short,default,long >/dev/null

docker run -d \
	--name "${SCHEDULER_CONTAINER}" \
	--network "${NETWORK_NAME}" \
	-v "${SITES_VOLUME}:/home/frappe/frappe-bench/sites" \
	"${common_frappe_env[@]}" \
	"${IMAGE_TAG}" \
	bench schedule >/dev/null

docker run -d \
	--name "${FRONTEND_CONTAINER}" \
	--network "${NETWORK_NAME}" \
	-p "${FRONTEND_PORT}:8080" \
	-v "${SITES_VOLUME}:/home/frappe/frappe-bench/sites" \
	"${common_frappe_env[@]}" \
	-e "BACKEND=${BACKEND_CONTAINER}:8000" \
	-e "SOCKETIO=${WEBSOCKET_CONTAINER}:9000" \
	-e "FRAPPE_SITE_NAME_HEADER=${SITE_NAME}" \
	"${IMAGE_TAG}" \
	nginx-entrypoint.sh >/dev/null

echo "Waiting for frontend at http://127.0.0.1:${FRONTEND_PORT}/api/method/ping ..."
wait_for_http "http://127.0.0.1:${FRONTEND_PORT}/api/method/ping" 420

cat <<EOF

Local smoke test is up.

URL:
  http://127.0.0.1:${FRONTEND_PORT}

Expected checks:
  - Open the URL and confirm the login page loads.
  - Visit http://127.0.0.1:${FRONTEND_PORT}/api/method/ping and expect {"message":"pong"}.
  - Inspect logs with:
      docker logs -f ${BACKEND_CONTAINER}
      docker logs -f ${FRONTEND_CONTAINER}

Cleanup:
  ./deployment/railway/scripts/local-smoke-test-down.sh

EOF
