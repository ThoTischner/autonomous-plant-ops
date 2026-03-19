FROM n8nio/n8n:latest

COPY workflows/ /workflows/
COPY entrypoint.sh /custom-entrypoint.sh

USER root
RUN chmod +x /custom-entrypoint.sh
USER node

ENTRYPOINT ["tini", "--", "/custom-entrypoint.sh"]
