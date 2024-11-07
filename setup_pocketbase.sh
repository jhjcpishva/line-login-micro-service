#!/bin/sh

# creates admin account for pocketbase
docker compose up pocketbase -d
docker compose exec pocketbase sh -c "pocketbase --dir=/pb_data admin create \$PB_ADMIN \$PB_PASSWORD"
# somehow pocketbase needs to be restarted
docker compose restart pocketbase

# creates initialize table
docker compose up app -d
docker compose exec app sh -c "python setup.py"
docker compose down
