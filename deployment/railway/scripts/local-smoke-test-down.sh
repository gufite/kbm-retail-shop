#!/usr/bin/env bash
set -euo pipefail

PROJECT_PREFIX="${PROJECT_PREFIX:-retail-railway-local}"

containers=(
	"${PROJECT_PREFIX}-frontend"
	"${PROJECT_PREFIX}-scheduler"
	"${PROJECT_PREFIX}-worker"
	"${PROJECT_PREFIX}-websocket"
	"${PROJECT_PREFIX}-backend"
	"${PROJECT_PREFIX}-redis"
	"${PROJECT_PREFIX}-mariadb"
)

for name in "${containers[@]}"; do
	if docker ps -a --format '{{.Names}}' | grep -Fxq "${name}"; then
		docker rm -f "${name}" >/dev/null
	fi
done

echo "Containers removed."
echo "Volumes and network are preserved:"
echo "  ${PROJECT_PREFIX}-db"
echo "  ${PROJECT_PREFIX}-redis"
echo "  ${PROJECT_PREFIX}-sites"
echo "  ${PROJECT_PREFIX}-net"
