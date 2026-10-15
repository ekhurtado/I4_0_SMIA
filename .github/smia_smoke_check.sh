#!/usr/bin/env bash
# SMIA Docker smoke test.
# Replicates examples/docker_compose_deployment/docker-compose.yml:
# ephemeral ejabberd + SMIA container with SMIA_tutorial_1.aasx.
# Success when container logs contain at least one of:
#   ## STATE 2: RUNNING ##  |  ACLHandlingBehaviour starting
#
# Env vars:
#   SMIA_IMAGE   (required) image under test, e.g. smia:test-alpine-base
#   SMOKE_TIMEOUT (optional, default 120 seconds)
#
# Usage:
#   SMIA_IMAGE=smia:test-alpine-base bash .github/smia_smoke_check.sh
set -u

TIMEOUT="${SMOKE_TIMEOUT:-120}"
INTERVAL=3
ELAPSED=0
EXPECTED1='## STATE 2: RUNNING ##'
EXPECTED2='ACLHandlingBehaviour starting'

if [ -z "${SMIA_IMAGE:-}" ]; then
  echo "::error::SMIA_IMAGE env var is not set (e.g. SMIA_IMAGE=smia:test-alpine-base)"
  exit 1
fi

NET="smia-smoke-$(date +%s)-$RANDOM"
EJABBERD_C="ejabberd-smoke-$RANDOM"
SMIA_C="smia-smoke-$RANDOM"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "Creating network $NET ..."
docker network create "$NET" >/dev/null

echo "Starting ephemeral ejabberd ($EJABBERD_C) ..."
# --hostname/--network-alias ejabberd: the SMIA JID domain (smiatest@ejabberd)
# must resolve to this container, as with container_name: ejabberd in the example compose.
docker run -d --name "$EJABBERD_C" --hostname ejabberd --network "$NET" --network-alias ejabberd \
  -v "$REPO_ROOT/examples/docker_compose_deployment/xmpp_server/ejabberd.yml:/opt/ejabberd/conf/ejabberd.yml:ro" \
  -e ERLANG_NODE_ARG=admin@ejabberd \
  -e ERLANG_COOKIE=dummycookie123 \
  ghcr.io/processone/ejabberd:latest >/dev/null

echo "Waiting for ejabberd port 5222 (max ~30s) ..."
for i in $(seq 1 15); do
  if docker exec "$EJABBERD_C" sh -c "netstat -ln 2>/dev/null | grep -q 5222 || ss -ln 2>/dev/null | grep -q 5222"; then
    echo "ejabberd is listening on 5222."
    break
  fi
  sleep 2
  if [ "$i" = "15" ]; then
    echo "::warning::ejabberd did not report 5222 as listening, continuing anyway."
  fi
done

echo "Waiting for ejabberd node readiness (ejabberdctl status, max ~60s) ..."
READY=false
for i in $(seq 1 30); do
  if docker exec "$EJABBERD_C" ejabberdctl status >/dev/null 2>&1; then
    echo "ejabberd node is ready."
    READY=true
    break
  fi
  sleep 2
done
if [ "$READY" != "true" ]; then
  echo "::error::ejabberd node never became ready. Dumping logs:"
  docker logs "$EJABBERD_C" 2>&1 | tail -n 100 || true
  docker rm -f "$EJABBERD_C" >/dev/null 2>&1 || true
  docker network rm "$NET" >/dev/null 2>&1 || true
  exit 1
fi

# Register the test user and verify it (no silent swallowing: SMIA must not
# depend on in-band registration alone).
if docker exec "$EJABBERD_C" ejabberdctl register smiatest ejabberd smiatest1234 >/dev/null 2>&1; then
  echo "Test user smiatest@ejabberd registered."
elif docker exec "$EJABBERD_C" ejabberdctl check_account smiatest ejabberd >/dev/null 2>&1; then
  echo "Test user smiatest@ejabberd already exists."
else
  echo "::error::Could not register nor verify test user smiatest@ejabberd. Dumping logs:"
  docker logs "$EJABBERD_C" 2>&1 | tail -n 100 || true
  docker rm -f "$EJABBERD_C" >/dev/null 2>&1 || true
  docker network rm "$NET" >/dev/null 2>&1 || true
  exit 1
fi

echo "Checking DNS: ejabberd must resolve from the SMIA side ..."
if ! docker run --rm --network "$NET" alpine getent hosts ejabberd; then
  echo "::error::Hostname 'ejabberd' does not resolve inside network $NET."
  docker rm -f "$EJABBERD_C" >/dev/null 2>&1 || true
  docker network rm "$NET" >/dev/null 2>&1 || true
  exit 1
fi

sleep 3

echo "Starting SMIA container ($SMIA_C) from image $SMIA_IMAGE ..."
docker run -d --name "$SMIA_C" --network "$NET" \
  -e AAS_MODEL_NAME=SMIA_tutorial_1.aasx \
  -e AGENT_ID=smiatest@ejabberd \
  -e AGENT_PSSWD=smiatest1234 \
  -v "$REPO_ROOT/examples/docker_compose_deployment/aas:/smia_archive/config/aas:ro" \
  "$SMIA_IMAGE" python3 -m smia.launchers.smia_docker_starter >/dev/null

echo "Waiting up to ${TIMEOUT}s for smoke strings ..."
while [ "$ELAPSED" -lt "$TIMEOUT" ]; do
  if ! docker inspect -f '{{.State.Running}}' "$SMIA_C" 2>/dev/null | grep -q true; then
    EXIT_CODE="$(docker inspect -f '{{.State.ExitCode}}' "$SMIA_C" 2>/dev/null || echo '?')"
    echo "::error::SMIA container died early (exit=$EXIT_CODE). Dumping logs:"
    echo "=== SMIA LOGS ==="
    docker logs "$SMIA_C" 2>&1 | tail -n 300 || true
    echo "=== EJABBERD LOGS ==="
    docker logs "$EJABBERD_C" 2>&1 | tail -n 100 || true
    docker rm -f "$SMIA_C" "$EJABBERD_C" >/dev/null 2>&1 || true
    docker network rm "$NET" >/dev/null 2>&1 || true
    exit 1
  fi
  LOGS="$(docker logs "$SMIA_C" 2>&1 || true)"
  if echo "$LOGS" | grep -qF "$EXPECTED1" || echo "$LOGS" | grep -qF "$EXPECTED2"; then
    echo "SMOKE OK: expected string found."
    echo "$LOGS" | tail -n 50
    docker rm -f "$SMIA_C" "$EJABBERD_C" >/dev/null 2>&1 || true
    docker network rm "$NET" >/dev/null 2>&1 || true
    exit 0
  fi
  sleep "$INTERVAL"
  ELAPSED=$((ELAPSED + INTERVAL))
done

echo "::error::Timeout of ${TIMEOUT}s reached without expected logs. Dumping logs:"
echo "=== SMIA LOGS ==="
docker logs "$SMIA_C" 2>&1 | tail -n 300 || true
echo "=== EJABBERD LOGS ==="
docker logs "$EJABBERD_C" 2>&1 | tail -n 100 || true
docker rm -f "$SMIA_C" "$EJABBERD_C" >/dev/null 2>&1 || true
docker network rm "$NET" >/dev/null 2>&1 || true
exit 1
