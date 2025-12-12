#!/bin/bash -e

cat <<EOF > .env
SECRET_KEY=$(openssl rand -hex 32)"
EOF
