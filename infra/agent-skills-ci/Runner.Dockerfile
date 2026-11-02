FROM node:24-bookworm-slim AS node
FROM ghcr.io/actions/actions-runner:2.338.1
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-venv python3-pip build-essential libssl-dev libyaml-dev \
    zlib1g-dev libffi-dev libreadline-dev libgmp-dev curl ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /opt/hostedtoolcache \
    && chown runner:runner /opt/hostedtoolcache
COPY --from=node /usr/local/bin/node /usr/local/bin/node
COPY --from=node /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -s /usr/local/lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \
    && ln -s /usr/local/lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx
RUN mv /home/runner /opt/runner-template && mkdir /home/runner && chown runner:runner /home/runner
USER runner
WORKDIR /home/runner
