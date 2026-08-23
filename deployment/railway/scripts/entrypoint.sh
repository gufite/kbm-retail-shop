#!/usr/bin/env bash
set -euo pipefail

BENCH_PATH=${BENCH_PATH:-/home/frappe/frappe-bench}
SITES_DIR=${SITES_DIR:-"${BENCH_PATH}/sites"}
ASSETS_PATH="${SITES_DIR}/assets"
BAKED_ASSETS_PATH="${BENCH_PATH}/assets"

SITE_NAME=${SITE_NAME:?SITE_NAME is required}
DB_HOST=${DB_HOST:?DB_HOST is required}
DB_PORT=${DB_PORT:-3306}
DB_ROOT_USER=${DB_ROOT_USER:-root}
DB_ROOT_PASSWORD=${DB_ROOT_PASSWORD:?DB_ROOT_PASSWORD is required}
DB_TYPE=${DB_TYPE:-mariadb}
SOCKETIO_PORT=${SOCKETIO_PORT:-9000}
BACKGROUND_WORKERS=${BACKGROUND_WORKERS:-1}

REDIS_CACHE_HOST=${REDIS_CACHE_HOST:-redis}
REDIS_CACHE_PORT=${REDIS_CACHE_PORT:-6379}
REDIS_QUEUE_HOST=${REDIS_QUEUE_HOST:-${REDIS_CACHE_HOST}}
REDIS_QUEUE_PORT=${REDIS_QUEUE_PORT:-${REDIS_CACHE_PORT}}
REDIS_SOCKETIO_HOST=${REDIS_SOCKETIO_HOST:-${REDIS_QUEUE_HOST}}
REDIS_SOCKETIO_PORT=${REDIS_SOCKETIO_PORT:-${REDIS_QUEUE_PORT}}

REDIS_CACHE_URL=${REDIS_CACHE_URL:-redis://${REDIS_CACHE_HOST}:${REDIS_CACHE_PORT}}
REDIS_QUEUE_URL=${REDIS_QUEUE_URL:-redis://${REDIS_QUEUE_HOST}:${REDIS_QUEUE_PORT}}
REDIS_SOCKETIO_URL=${REDIS_SOCKETIO_URL:-redis://${REDIS_SOCKETIO_HOST}:${REDIS_SOCKETIO_PORT}}

mkdir -p "${SITES_DIR}" "${BENCH_PATH}/logs"

rm -rf "${ASSETS_PATH}"
ln -s "${BAKED_ASSETS_PATH}" "${ASSETS_PATH}"

cd "${BENCH_PATH}"

ls -1 apps > "${SITES_DIR}/apps.txt"

bench set-config -g db_host "${DB_HOST}"
bench set-config -gp db_port "${DB_PORT}"
bench set-config -g db_type "${DB_TYPE}"
bench set-config -g redis_cache "${REDIS_CACHE_URL}"
bench set-config -g redis_queue "${REDIS_QUEUE_URL}"
bench set-config -g redis_socketio "${REDIS_SOCKETIO_URL}"
bench set-config -gp socketio_port "${SOCKETIO_PORT}"
bench set-config -gp background_workers "${BACKGROUND_WORKERS}"
bench set-config -g serve_default_site true
bench set-config -g default_site "${SITE_NAME}"

printf '%s\n' "${SITE_NAME}" > "${SITES_DIR}/currentsite.txt"

wait-for-it "${DB_HOST}:${DB_PORT}" -t 120
wait-for-it "${REDIS_CACHE_HOST}:${REDIS_CACHE_PORT}" -t 120

if [ "${REDIS_QUEUE_HOST}:${REDIS_QUEUE_PORT}" != "${REDIS_CACHE_HOST}:${REDIS_CACHE_PORT}" ]; then
	wait-for-it "${REDIS_QUEUE_HOST}:${REDIS_QUEUE_PORT}" -t 120
fi

if [ "${REDIS_SOCKETIO_HOST}:${REDIS_SOCKETIO_PORT}" != "${REDIS_QUEUE_HOST}:${REDIS_QUEUE_PORT}" ] && \
	[ "${REDIS_SOCKETIO_HOST}:${REDIS_SOCKETIO_PORT}" != "${REDIS_CACHE_HOST}:${REDIS_CACHE_PORT}" ]; then
	wait-for-it "${REDIS_SOCKETIO_HOST}:${REDIS_SOCKETIO_PORT}" -t 120
fi

/usr/local/bin/railway-bootstrap.sh

exec "$@"
