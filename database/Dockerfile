FROM postgres:15-alpine

ENV POSTGRES_USER=riya
ENV POSTGRES_PASSWORD=riya123
ENV POSTGRES_DB=riyadb

COPY init.sql /docker-entrypoint-initdb.d/init.sql

EXPOSE 5432