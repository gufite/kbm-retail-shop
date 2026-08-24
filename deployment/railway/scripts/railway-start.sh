#!/usr/bin/env bash
set -uo pipefail

# Railway does not support attaching one volume to multiple services, so all
# Frappe processes (web, realtime, background workers, scheduler, nginx) run
# together in this single container/service instead of being split across
# separate Railway services that would otherwise need a shared sites volume.

export BACKEND=${BACKEND:-127.0.0.1:8000}
export SOCKETIO=${SOCKETIO:-127.0.0.1:9000}
BACKGROUND_WORKERS=${BACKGROUND_WORKERS:-1}

pids=()
declare -A pid_names

start() {
	local name="$1"
	shift
	"$@" &
	local pid=$!
	pids+=("${pid}")
	pid_names["${pid}"]="${name}"
	echo "Started ${name} (pid ${pid}): $*"
}

start gunicorn /usr/local/bin/start.sh
start socketio node /home/frappe/frappe-bench/apps/frappe/socketio.js

# Plain `bench worker`, not `bench worker-pool`: worker-pool's FrappeWorker
# auto-starts its own scheduler thread per worker (an experimental feature),
# which races the dedicated `bench schedule` process below for the same
# lock file and makes it exit immediately, believing another instance is
# already running.
for i in $(seq 1 "${BACKGROUND_WORKERS}"); do
	start "worker-${i}" bench worker --queue short,default,long
done

start schedule bench schedule
start nginx /usr/local/bin/nginx-entrypoint.sh

shutdown() {
	trap - TERM INT
	echo "Shutting down supervised processes..."
	kill "${pids[@]}" 2>/dev/null || true
	wait
}
trap shutdown TERM INT

exited_pid=""
wait -n -p exited_pid
exit_code=$?

echo "${pid_names[${exited_pid}]:-unknown} (pid ${exited_pid}) exited (code ${exit_code}); stopping the rest."
shutdown
exit "${exit_code}"
