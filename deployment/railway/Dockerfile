ARG FRAPPE_IMAGE_PREFIX=frappe
ARG FRAPPE_BRANCH=version-15
ARG FRAPPE_PATH=https://github.com/frappe/frappe

FROM ${FRAPPE_IMAGE_PREFIX}/build:${FRAPPE_BRANCH} AS builder

ARG FRAPPE_BRANCH=version-15
ARG FRAPPE_PATH=https://github.com/frappe/frappe

USER frappe

COPY --chown=frappe:frappe apps.json /opt/frappe/apps.json

RUN bench init \
	--apps_path=/opt/frappe/apps.json \
	--frappe-branch="${FRAPPE_BRANCH}" \
	--frappe-path="${FRAPPE_PATH}" \
	--no-procfile \
	--no-backups \
	--skip-redis-config-generation \
	--verbose \
	/home/frappe/frappe-bench && \
	cd /home/frappe/frappe-bench && \
	echo "{}" > sites/common_site_config.json && \
	find apps -mindepth 1 -path "*/.git" -prune -exec rm -rf {} +

# apps.json does not change on every push, so the bench-init layer above is
# cached with a stale retail_shop clone. Re-install this app on every commit
# so kbmlight.com actually receives the code that was just pushed.
ARG RAILWAY_GIT_COMMIT_SHA=unknown
ADD https://api.github.com/repos/gufite/kbm-retail-shop/commits/main /tmp/kbm-retail-shop-head.json
RUN echo "Installing retail_shop ${RAILWAY_GIT_COMMIT_SHA}" \
	&& cd /home/frappe/frappe-bench \
	&& rm -rf apps/retail_shop \
	&& bench get-app --branch main https://github.com/gufite/kbm-retail-shop.git \
	&& bench build --app retail_shop \
	&& find apps/retail_shop -path "*/.git" -prune -exec rm -rf {} +

FROM ${FRAPPE_IMAGE_PREFIX}/base:${FRAPPE_BRANCH} AS backend

USER frappe

COPY --from=builder --chown=frappe:frappe /home/frappe/frappe-bench /home/frappe/frappe-bench

WORKDIR /home/frappe/frappe-bench

RUN cp -r /home/frappe/frappe-bench/sites/assets /home/frappe/frappe-bench/assets && \
	rm -rf /home/frappe/frappe-bench/sites/assets

# No VOLUME instruction: Railway's Dockerfile builder rejects it outright.
# Persistence is provided by attaching a Railway Volume to
# /home/frappe/frappe-bench/sites on each Frappe service instead.

USER root

COPY scripts/entrypoint.sh /usr/local/bin/entrypoint.sh
COPY scripts/bootstrap.sh /usr/local/bin/railway-bootstrap.sh
COPY scripts/start.sh /usr/local/bin/start.sh
COPY scripts/railway-start.sh /usr/local/bin/railway-start.sh

RUN chmod 755 /usr/local/bin/entrypoint.sh /usr/local/bin/railway-bootstrap.sh /usr/local/bin/start.sh /usr/local/bin/railway-start.sh

# Railway volumes are root-owned when first attached; startup initializes the
# mounted sites directory before Frappe processes are launched.
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["railway-start.sh"]
