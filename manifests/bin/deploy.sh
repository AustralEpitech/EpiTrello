#!/bin/bash -e
set -o pipefail

kapply() {
    local f; for f in "$@"; do
        kubectl apply --server-side \
            -f<(envsubst "$(env | sed 's/^/$/')" < "manifests/$f")
    done
}; export -f kapply

kcreatesec() {
    kubectl apply --server-side \
        -f<(kubectl create secret generic --dry-run=client -oyaml "$@")
}; export -f kcreatesec

kcreatecm() {
    kubectl apply --server-side \
        -f<(kubectl create configmap --dry-run=client -oyaml "$@")
}; export -f kcreatecm

kgseckey() {
    local sec="$1"; shift
    local key="$1"; shift

    kubectl get secret "$sec" -ojson | jq -re ".data.\"$key\"" | base64 -d
}; export -f kgseckey

kgcmkey() {
    local cm="$1";  shift
    local key="$1"; shift

    kubectl get configmap "$cm" -ojson | jq -re ".data.\"$key\""
}; export -f kgcmkey

krm() {
    kubectl delete --ignore-not-found=true "${@/#/-fmanifests/}"
}; export -f krm


krm common/job.yaml

kapply common/db.yaml

kubectl wait --for=condition=Ready --timeout=300s cluster/postgres

kcreatesec django \
    --from-literal=SECRET_KEY="$(kgseckey django SECRET_KEY || openssl rand -hex 32)" \
    --from-literal=ALLOWED_HOSTS="$BASE_URL"

kcreatesec anubis \
    --from-literal=ED25519_PRIVATE_KEY_HEX="$(kgseckey anubis ED25519_PRIVATE_KEY_HEX || openssl rand -hex 32)"

kapply common/job.yaml common/valkey.yaml common/app.yaml
