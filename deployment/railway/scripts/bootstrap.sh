#!/usr/bin/env bash
set -euo pipefail

BENCH_PATH=${BENCH_PATH:-/home/frappe/frappe-bench}
SITES_DIR=${SITES_DIR:-"${BENCH_PATH}/sites"}
SITE_NAME=${SITE_NAME:?SITE_NAME is required}
DB_TYPE=${DB_TYPE:-mariadb}
DB_HOST=${DB_HOST:?DB_HOST is required}
DB_PORT=${DB_PORT:-3306}
DB_ROOT_USER=${DB_ROOT_USER:-root}
DB_ROOT_PASSWORD=${DB_ROOT_PASSWORD:?DB_ROOT_PASSWORD is required}
INSTALL_APPS=${INSTALL_APPS:-erpnext,retail_shop}

site_config="${SITES_DIR}/${SITE_NAME}/site_config.json"
lock_root="${SITES_DIR}/.railway-locks"
bootstrap_lock="${lock_root}/bootstrap"
migrate_lock="${lock_root}/migrate"
lock_wait_timeout=${LOCK_WAIT_TIMEOUT:-900}

mkdir -p "${lock_root}"
cd "${BENCH_PATH}"

trim() {
	local value="$1"
	value="${value#"${value%%[![:space:]]*}"}"
	value="${value%"${value##*[![:space:]]}"}"
	printf '%s' "${value}"
}

build_install_args() {
	local IFS=','
	local app
	local -a args=()
	read -r -a apps <<< "${INSTALL_APPS}"

	for app in "${apps[@]}"; do
		app="$(trim "${app}")"
		if [ -n "${app}" ]; then
			args+=("--install-app" "${app}")
		fi
	done

	printf '%s\0' "${args[@]}"
}

wait_for_lock() {
	local lock_path="$1"
	local elapsed=0

	until mkdir "${lock_path}" 2>/dev/null; do
		sleep 5
		elapsed=$((elapsed + 5))
		if [ "${elapsed}" -ge "${lock_wait_timeout}" ]; then
			echo "Timed out waiting for lock ${lock_path}" >&2
			exit 1
		fi
	done
}

release_lock() {
	local lock_path="$1"
	rmdir "${lock_path}" 2>/dev/null || true
}

create_site_if_missing() {
	if [ -f "${site_config}" ]; then
		return
	fi

	: "${ADMIN_PASSWORD:?ADMIN_PASSWORD is required when AUTO_SETUP_SITE=1}"

	wait_for_lock "${bootstrap_lock}"
	trap 'release_lock "${bootstrap_lock}"' EXIT

	if [ ! -f "${site_config}" ]; then
		local -a install_args=()
		mapfile -d '' install_args < <(build_install_args)

		local -a create_args=(
			"--db-type" "${DB_TYPE}"
			"--db-host" "${DB_HOST}"
			"--db-port" "${DB_PORT}"
			"--db-root-username" "${DB_ROOT_USER}"
			"--db-root-password" "${DB_ROOT_PASSWORD}"
			"--admin-password" "${ADMIN_PASSWORD}"
			"--set-default"
		)

		if [ "${DB_TYPE}" = "mariadb" ]; then
			create_args+=("--mariadb-user-host-login-scope=%")
		fi

		create_args+=("${install_args[@]}")
		create_args+=("${SITE_NAME}")

		bench new-site "${create_args[@]}"
	fi

	release_lock "${bootstrap_lock}"
	trap - EXIT
}

migrate_site_if_requested() {
	if [ "${AUTO_MIGRATE:-0}" != "1" ]; then
		return
	fi

	if [ ! -f "${site_config}" ]; then
		echo "Skipping migrate because ${SITE_NAME} is not initialized yet." >&2
		return
	fi

	wait_for_lock "${migrate_lock}"
	trap 'release_lock "${migrate_lock}"' EXIT

	bench --site "${SITE_NAME}" migrate

	release_lock "${migrate_lock}"
	trap - EXIT
}

if [ "${AUTO_SETUP_SITE:-0}" = "1" ]; then
	create_site_if_missing
fi

migrate_site_if_requested
