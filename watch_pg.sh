#!/bin/bash


while :; do
    #docker compose exec db psql postgresql://postgres:postgres@localhost/postgres -c "select count(*) from pg_stat_activity where query like '%pg_sleep%';"
    docker compose exec db psql postgresql://postgres:postgres@localhost/postgres -c "select count(*) from pg_stat_activity where datname = 'postgres'"
    sleep 2;
done
