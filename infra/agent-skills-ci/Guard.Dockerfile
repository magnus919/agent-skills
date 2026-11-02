FROM alpine:3.23
RUN apk add --no-cache iptables
COPY guard.sh /guard.sh
ENTRYPOINT ["/bin/sh", "/guard.sh"]
