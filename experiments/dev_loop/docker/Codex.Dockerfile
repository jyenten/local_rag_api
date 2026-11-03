FROM node:22-bookworm-slim

# Native Codex HTTPS uses system trust, unlike Node's bundled CA store.
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl \
    && update-ca-certificates \
    && test -s /etc/ssl/certs/ca-certificates.crt \
    && rm -rf /var/lib/apt/lists/*

# Separate from the offline checker: this image needs model-network access.
RUN npm install --global @openai/codex@0.162.1 \
    && npm cache clean --force \
    && codex --version \
    && mkdir -p /home/node/.codex /work \
    && chown 1000:1000 /home/node/.codex /work

ENV HOME=/home/node CODEX_HOME=/home/node/.codex SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
COPY docker/response.schema.json /opt/codex-lab/response.schema.json
COPY docker/files.schema.json /opt/codex-lab/files.schema.json
USER 1000:1000
WORKDIR /work
ENTRYPOINT ["codex"]
