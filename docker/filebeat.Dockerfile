FROM docker.elastic.co/beats/filebeat:8.7.1

COPY filebeat.yml /usr/share/filebeat/filebeat.yml
USER root
# Work on windows
# RUN filebeat -e --strict.perms=false
# Work on Ubuntu
# RUN chown -R root /usr/share/filebeat/
# RUN chmod -R go-w /usr/share/filebeat/
