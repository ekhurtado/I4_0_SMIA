/**
 * Infrastructure Docker Compose Data
 * ====================================
 * Service definitions embedded as JavaScript constants, split by domain so
 * they can be read by the SMIA Environment Builder without needing HTTP
 * fetch() (which fails with file:// protocol due to CORS):
 *   - INFRA_BASYX_JAVA_YAML: BaSyx Java services (aas-env, registries, mongo, UI)
 *   - INFRA_BASYX_GO_YAML:   BaSyx Go services (aas-environment, postgres, UI)
 *   - INFRA_XMPP_YAML:        Ejabberd XMPP server
 *   - INFRA_SMIA_YAML:        SMIA services (smia-ism + smia-i-kb template,
 *                             parametrized per BaSyx variant)
 * Plus EJABBERD_YAML (ejabberd.yml) and BASYX_GO_RSA_KEY (rsa-key.pem).
 */

const INFRA_BASYX_JAVA_YAML = `# ----------------------------------------
# AAS Infrastructure services (BaSyx Java)
# ----------------------------------------
aas-env:
  image: eclipsebasyx/aas-environment:2.0.0-SNAPSHOT
  container_name: aas-env
  environment:
    - SERVER_PORT=8081
  volumes:
    - ./aas:/application/aas
    - ./basyx/aas-env.properties:/application/application.properties
  ports:
    - '8081:8081'
  restart: always
  depends_on:
    aas-registry:
      condition: service_healthy
    sm-registry:
      condition: service_healthy
    mongo:
      condition: service_healthy

aas-registry:
  image: eclipsebasyx/aas-registry-log-mongodb:2.0.0-SNAPSHOT
  container_name: aas-registry
  ports:
    - '8082:8080'
  environment:
    - SERVER_PORT=8080
  volumes:
    - ./basyx/aas-registry.yml:/workspace/config/application.yml
  restart: always
  depends_on:
    mongo:
      condition: service_healthy

sm-registry:
  image: eclipsebasyx/submodel-registry-log-mongodb:2.0.0-SNAPSHOT
  container_name: sm-registry
  ports:
    - '8083:8080'
  environment:
    - SERVER_PORT=8080
  volumes:
    - ./basyx/sm-registry.yml:/workspace/config/application.yml
  restart: always
  depends_on:
    mongo:
      condition: service_healthy

mongo:
  image: mongo:5.0.10
  container_name: mongo
  environment:
    MONGO_INITDB_ROOT_USERNAME: mongoAdmin
    MONGO_INITDB_ROOT_PASSWORD: mongoPassword
  restart: always
  healthcheck:
    test: mongo
    interval: 10s
    timeout: 5s
    retries: 5

aas-web-ui:
  image: eclipsebasyx/aas-gui:SNAPSHOT
  container_name: aas-ui
  ports:
    - '3000:3000'
  environment:
    AAS_REGISTRY_PATH: http://localhost:8082/shell-descriptors
    SUBMODEL_REGISTRY_PATH: http://localhost:8083/submodel-descriptors
    AAS_REPO_PATH: http://localhost:8081/shells
    SUBMODEL_REPO_PATH: http://localhost:8081/submodels
    CD_REPO_PATH: http://localhost:8081/concept-descriptions
    AAS_DISCOVERY_PATH: http://localhost:8084/lookup/shells
    PRIMARY_COLOR: '#347EE1'
    LOGO_PATH: SMIA_logo.ico
  restart: always
  depends_on:
    aas-env:
      condition: service_healthy
  volumes:
    - ./logo:/usr/src/app/dist/Logo
`;

/**
 * BaSyx Go variant service definitions.
 * ======================================
 * Lighter-weight Go implementation promoted by BaSyx (unified aas-environment
 * on port 8082 + Postgres backend). Used when the user selects BaSyx Go.
 * NOTE: the aas-ui volume points to ./basyx/basyx-infra.yml (inside the
 * generated basyx/ folder), unlike the standalone example using the ZIP root.
 */
const INFRA_BASYX_GO_YAML = `# ----------------------------------------
# AAS Infrastructure services (BaSyx Go)
# ----------------------------------------
aas-environment:
  image: eclipsebasyx/aasenvironment-go:1.1.2
  container_name: aas-environment
  pull_policy: always
  ports:
    - 8082:8082
  environment:
    - LOGGING_FORMAT=text
    - LOGGING_LEVEL=info
    - SERVER_PORT=8082
    - SERVER_CACHEENABLED=false
    - SERVER_STRICTVERIFICATION=off
    - SERVER_VERIFICATIONENDPOINTAVAILABLE=false
    - SERVER_READ_HEADER_TIMEOUT_SECONDS=15
    - SERVER_READ_TIMEOUT_SECONDS=300
    - SERVER_WRITE_TIMEOUT_SECONDS=300
    - SERVER_IDLE_TIMEOUT_SECONDS=60
    - SERVER_SHUTDOWN_TIMEOUT_SECONDS=10
    - SERVER_PAGINATION_DEFAULT_LIMIT=100
    - SERVER_PAGINATION_MAX_LIMIT=1000
    - CORS_ALLOWEDORIGINS=*
    - CORS_ALLOWEDHEADERS=*
    - CORS_ALLOWCREDENTIALS=true
    - CORS_ALLOWEDMETHODS=GET,POST,PUT,PATCH,DELETE,OPTIONS
    - POSTGRES_HOST=db
    - POSTGRES_PORT=5432
    - POSTGRES_USER=admin
    - POSTGRES_PASSWORD=admin123
    - POSTGRES_DBNAME=basyxTestDB
    - POSTGRES_SSLMODE=disable
    - POSTGRES_CONNECTTIMEOUTSECONDS=0
    - POSTGRES_MAXOPENCONNECTIONS=50
    - POSTGRES_MAXIDLECONNECTIONS=25
    - POSTGRES_CONNMAXLIFETIMEMINUTES=5
    - POSTGRES_CONNMAXIDLETIMEMINUTES=0
    - JWS_PRIVATEKEYPATH=/app/rsa-key.pem
    - ABAC_ENABLED=false
    - GENERAL_ENABLEIMPLICITCASTS=true
    - GENERAL_ENABLEDESCRIPTORDEBUG=false
    - GENERAL_ENABLECUSTOMMIDDLEWAREHEADERINJECTION=false
    - GENERAL_SUPPORTSSINGULARSUPPLEMENTALSEMANTICID=false
    - GENERAL_TRUSTPROXYHEADERS=false
    - GENERAL_UPLOADMAXSIZEBYTES=134217728
    - GENERAL_DELEGATEDOPERATIONRESPONSEMAXSIZEBYTES=1048576
    - GENERAL_AASXMAXPARTCOUNT=10000
    - GENERAL_AASXMAXOPCMETADATASIZEBYTES=16777216
    - GENERAL_AASXMAXPARTEXPANDEDSIZEBYTES=134217728
    - GENERAL_AASXMAXTOTALEXPANDEDSIZEBYTES=536870912
    - GENERAL_AASXMAXTHUMBNAILSIZEBYTES=16777216
    - GENERAL_BULK_BATCH_LIMIT=1000
    - GENERAL_AASREGISTRYINTEGRATION=true
    - GENERAL_SUBMODELREGISTRYINTEGRATION=true
    - GENERAL_DISCOVERYINTEGRATION=true
    - GENERAL_EXTERNALURL=http://localhost:8082
    - GENERAL_AAS_PRECONFIG_PATHS=/app/preconfiguration
    - BASYX_HISTORY_MODE=off
    - BASYX_HISTORY_RETENTION_DAYS=0
    - BASYX_HISTORY_FULL_SNAPSHOT_INTERVAL=1
    - BASYX_HISTORY_IMMUTABILITY=none
    - BASYX_AUDIT_IDENTITY_MODE=none
    - BASYX_HISTORY_EVIDENCE_ENABLED=false
    - BASYX_HISTORY_INTEGRITY_ANCHOR_PROVIDER=none
    - BASYX_EVENTING_ENABLED=false
    - BASYX_EVENTING_FORMAT=cloudevents
    - BASYX_EVENTING_OUTBOX_ENABLED=false
    - BASYX_EVENTING_TOPIC_PREFIX=basyx
    - BASYX_EVENTING_FEED_ENABLED=false
    - OTEL_TRACES_EXPORTER=none
    - OTEL_METRICS_EXPORTER=none
    - GENERAL_TRUSTEDPROXYCIDRS=
    - POSTGRES_SEARCHPATH=
    - POSTGRES_TIMEZONE=
    - OTEL_SERVICE_NAME=aasenvironmentservice
    - OTEL_TRACES_SAMPLER=parentbased_always_on
    - OTEL_PROPAGATORS=tracecontext,baggage
  volumes:
    - ./basyx/rsa-key.pem:/app/rsa-key.pem:ro
    - ./aas:/app/preconfiguration:ro
  depends_on:
    basyx_configuration:
      condition: service_completed_successfully
  restart: unless-stopped
  labels: {}

db:
  container_name: postgres_db
  image: postgres:18
  environment:
    POSTGRES_USER: admin
    POSTGRES_PASSWORD: admin123
    POSTGRES_DB: basyxTestDB
  command:
    - postgres
    - -c
    - listen_addresses=*
  healthcheck:
    test:
      - CMD-SHELL
      - pg_isready -U admin -d basyxTestDB
    interval: 10s
    timeout: 5s
    retries: 5
  restart: unless-stopped

basyx_configuration:
  container_name: basyx_configuration
  image: eclipsebasyx/basyxconfigurationservice-go:1.1.2
  pull_policy: always
  environment:
    - POSTGRES_HOST=db
    - POSTGRES_PORT=5432
    - POSTGRES_USER=admin
    - POSTGRES_PASSWORD=admin123
    - POSTGRES_DBNAME=basyxTestDB
    - POSTGRES_SSLMODE=disable
    - POSTGRES_CONNECTTIMEOUTSECONDS=0
    - POSTGRES_MAXOPENCONNECTIONS=50
    - POSTGRES_MAXIDLECONNECTIONS=25
    - POSTGRES_CONNMAXLIFETIMEMINUTES=5
    - POSTGRES_CONNMAXIDLETIMEMINUTES=0
    - POSTGRES_SEARCHPATH=
    - POSTGRES_TIMEZONE=
  depends_on:
    db:
      condition: service_healthy
  labels: {}

aas-ui:
  container_name: aas-web-ui
  image: eclipsebasyx/aas-gui:latest
  pull_policy: always
  ports:
    - 3000:3000
  environment:
    ENDPOINT_CONFIG_AVAILABLE: 'false'
    ALLOW_EDITING: 'true'
    ALLOW_UPLOADING: 'true'
    ALLOW_LOGOUT: 'true'
    SM_VIEWER_EDITOR: 'true'
    START_PAGE_ROUTE_NAME: AASEditor
    PRIMARY_LIGHT_COLOR: '#0277BD'
    PRIMARY_DARK_COLOR: '#0277BD'
  volumes:
    - ./basyx/basyx-infra.yml:/basyx-infra.yml:ro
  depends_on:
    aas-environment:
      condition: service_started
  restart: unless-stopped
`;

/**
 * RSA private key for the BaSyx Go aas-environment (JWS signing).
 * Reused verbatim for every generated environment (dev/tutorial use).
 */
const BASYX_GO_RSA_KEY = `-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCXOMnXK4nPMsSd
b6QnflZuV7hXmx+OINutahyvm2qjxyu0zvE34INAaTe9NAypVJErzkKIVhv9AWzu
GkGtFD2xQ3AgOJ720BH+JAZgSeeYoaxPOa0Na9DfLYyFcNv8AS5mOtA0Q+wRiCGx
Aqd/v1UfFKcj+IoylPiVQlmYrrImzZj/ZwukeJNzt1nM7cBjYUlFlSj/znpaCif6
3NLpaBWQvNLZf0D5tcp1bl/GP79AyNIf9Fvqz3Pz4BGlHhF9/RF4Ti/m38O35bLR
hzwOirrOvWVyeyYXFYhLKhBSdrHMOJQ2ZIXh2OZOeNfTl/b60m9xhCvG2wQuJruF
pAj/FhGbAgMBAAECggEAK5KB2f1iDnEm5OQrrPOCrPWamKeKTpYaJhwKmvDRp9I2
PjlYmMyYlQEcPeiW8116HOCoHAePtfVosSygmuHXqtFvJ+GYsC4g2RUBP1JcKIcB
EqzgN5tGyl+h+zsbL8AZYfx1THH7vct3Rb0pjS4QtU1qoXs2Or/g5oUBMvS3QWWP
11b3FHq24Aj4UE7H6qtAy3LgR/n8B6jujFE40YfbYnQZ91kGybnoT91D75x00s1t
P3FyFUKbjWZ1LuwX9oK/XzGOO6Ht7vz+Ox4AA7Ct6FJq2Ad9QdcnH5IsHP6RJeD9
Bnb0yhAnLu2ozPj4XWl3mhZH59tL3xeOsUwQ+oPqCQKBgQDHzZq92zwBywLvOTTV
Bi69S454y7VBydJ+rd9N7NcWIwWxdcT6VhuprOvJaMx/4obwLKSyRQTF7JLrDYwE
4AeCtRCFM82/fBaTNfvHpAVQ/3QrID9bDhv0tZ0iZxB8tdScLwop0y8oMhSgoHP9
srDbhGEvdey5nIaQNJSLZAWaeQKBgQDBwTDo9wAZzoDT80ovMH+TunnswcpqRjKh
AeOCR1D2nMjnjNT834ALU261gbdS7VpU5n9T/HN28LjtHp6jai7SvnvCCrFO4qPh
jMBKZqXmoJJYHqwpX1b7wG07JoEmTDdJc5j5nT9hHC732NW/E8Nz5cpbqoSsgvON
o63RHw/HswKBgDZSZhHcOzJZmZCkwwJvzeFVW4ToDX23e21JpH6xN8EjAHdBB67w
HlFBXFHEFmVmlz1RRe3Z6fRN35vccQcaSbB1veoZLYU0HYcklDGxHGjrKxBWkiMV
cPBVOEWUM91UKlvURjUc36NUCluphB+jp4XnNe0LaLMGJWerg/9p0EQxAoGAG2Tn
N2kE2KE70bvKN1XSE97/shvMNK5sJhuQQTE4H0YXmbVtv7sR7YgEVSFb/BuW8/4K
7qL46E4st0nnAA/ZQu6vrMW6P/8HULKH1X0h47O8PT1I9iiGsd2JFB3jkLih8H6p
mFFFTsOfWGeOARAYSGCq9b7sNz/kk5ga0UBlCMUCgYEAhXktXzyhKIZXyhjdNx8L
6lDXZ+bXKKjYIj3UFfaq+P8uVg2nMYgV8tr0zZBi80v0/lhXzBK5hQ+G7hBOHXm3
jHhhb9PV28tPRosJtdbW3KeAjXHGoza104ZFm8nYXl5RvtZVqV9yJWeqvaNOYa/Z
TEXhhRrnEr8Ey7oghZlQLV0=
-----END PRIVATE KEY-----`;

/**
 * Ejabberd XMPP server service definition.
 */
const INFRA_XMPP_YAML = `# ----------------------------
# XMPP Server (Ejabberd)
# ----------------------------
xmpp-server:
  image: ghcr.io/processone/ejabberd
  container_name: ejabberd
  environment:
    - ERLANG_NODE_ARG=admin@ejabberd
    - ERLANG_COOKIE=dummycookie123
    - CTL_ON_CREATE=! register admin localhost asd
  ports:
    - "5222:5222"
    - "5269:5269"
    - "5280:5280"
    - "5443:5443"
  volumes:
    - ./xmpp_server/ejabberd.yml:/opt/ejabberd/conf/ejabberd.yml
  healthcheck:
    test: netstat -nl | grep -q 5222
    start_period: 5s
    interval: 5s
    timeout: 5s
    retries: 10
`;

/**
 * SMIA infrastructure service definitions.
 * ========================================
 * smia-i-kb is a template: __AAS_ENV_URL__ and __AAS_ENV_SERVICE__ are
 * replaced at generation time according to the selected BaSyx variant
 * (Java: http://aas-env:8081 / aas-env — Go: http://aas-environment:8082
 * / aas-environment).
 */
const INFRA_SMIA_YAML = `# ----------------------------
# SMIA Infrastructure services
# ----------------------------
smia-i-kb:
  image: ekhurtado/smia-tools:latest-smia-i-kb
  container_name: smia-i-kb
  ports:
    - '8090:8080'
  environment:
    - AAS_ENV_IP=__AAS_ENV_URL__
    #- SELF_EXTRACT_CSS=yes
  depends_on:
    __AAS_ENV_SERVICE__:
      condition: service_healthy
  healthcheck:
    test: wget --no-verbose --tries=1 --spider http://smia-i-kb:8080/api/v3/ui/ || exit 1
    interval: 10s
    timeout: 5s
    retries: 5
    start_period: 5s

smia-ism:
  image: ekhurtado/smia-tools:latest-smia-ism
  container_name: smia-ism
  environment:
    - AAS_MODEL_NAME=SMIA_InfrastructureServicesManager.aasx
    - AGENT_ID=smia-ism@ejabberd
    - AGENT_PSSWD=gciscedri1234
    - SMIA_KB_IP=http://smia-i-kb:8080
  depends_on:
    xmpp-server:
      condition: service_healthy
    smia-i-kb:
      condition: service_healthy
  healthcheck:
    test: exit 0
    start_period: 15s
  volumes:
    - ./aas:/smia_archive/config/aas
`;


const EJABBERD_YAML = `###
###              ejabberd configuration file
###
### The parameters used in this configuration file are explained at
###
###       https://docs.ejabberd.im/admin/configuration
###
### The configuration file is written in YAML.
### *******************************************************
### *******           !!! WARNING !!!               *******
### *******     YAML IS INDENTATION SENSITIVE       *******
### ******* MAKE SURE YOU INDENT SECTIONS CORRECTLY *******
### *******************************************************
### Refer to http://en.wikipedia.org/wiki/YAML for the brief description.
###

hosts:
  - localhost
  - ejabberd

loglevel: info

ca_file: /opt/ejabberd/conf/cacert.pem

certfiles:
  - /opt/ejabberd/conf/server.pem

## If you already have certificates, list them here
# certfiles:
#  - /etc/letsencrypt/live/domain.tld/fullchain.pem
#  - /etc/letsencrypt/live/domain.tld/privkey.pem

listen:
  -
    port: 5222
    ip: "::"
    module: ejabberd_c2s
    max_stanza_size: 262144
    shaper: c2s_shaper
    access: c2s
    starttls_required: true
  -
    port: 5223
    ip: "::"
    module: ejabberd_c2s
    max_stanza_size: 262144
    shaper: c2s_shaper
    access: c2s
    tls: true
  -
    port: 5269
    ip: "::"
    module: ejabberd_s2s_in
    max_stanza_size: 524288
    shaper: s2s_shaper
  -
    port: 5443
    ip: "::"
    module: ejabberd_http
    tls: true
    request_handlers:
      /admin: ejabberd_web_admin
      /api: mod_http_api
      /bosh: mod_bosh
      /captcha: ejabberd_captcha
      /upload: mod_http_upload
      /ws: ejabberd_http_ws
  -
    port: 5280
    ip: "::"
    module: ejabberd_http
    request_handlers:
      /admin: ejabberd_web_admin
      /.well-known/acme-challenge: ejabberd_acme
  -
    port: 3478
    ip: "::"
    transport: udp
    module: ejabberd_stun
    use_turn: true
    ## The server's public IPv4 address:
    # turn_ipv4_address: "203.0.113.3"
    ## The server's public IPv6 address:
    # turn_ipv6_address: "2001:db8::3"
  -
    port: 1883
    ip: "::"
    module: mod_mqtt
    backlog: 1000

s2s_use_starttls: optional

acl:
  local:
    user_regexp: ""
  loopback:
    ip:
      - 127.0.0.0/8
      - ::1/128

access_rules:
  local:
    allow: local
  c2s:
    deny: blocked
    allow: all
  announce:
    allow: admin
  configure:
    allow: admin
  muc_create:
    allow: local
  pubsub_createnode:
    allow: local
  trusted_network:
    allow: loopback

api_permissions:
  "console commands":
    from:
      - ejabberd_ctl
    who: all
    what: "*"
  "admin access":
    who:
      access:
        allow:
          - acl: loopback
          - acl: admin
      oauth:
        scope: "ejabberd:admin"
        access:
          allow:
            - acl: loopback
            - acl: admin
    what:
      - "*"
      - "!stop"
      - "!start"
  "public commands":
    who:
      ip: 127.0.0.1/8
    what:
      - status
      - connected_users_number

shaper:
  normal:
    rate: 3000
    burst_size: 20000
  fast: 100000

shaper_rules:
  max_user_sessions: 10
  max_user_offline_messages:
    5000: admin
    100: all
  c2s_shaper:
    none: admin
    normal: all
  s2s_shaper: fast

modules:
  mod_adhoc: {}
  mod_admin_extra: {}
  mod_announce:
    access: announce
  mod_avatar: {}
  mod_blocking: {}
  mod_bosh: {}
  mod_caps: {}
  mod_carboncopy: {}
  mod_client_state: {}
  mod_configure: {}
  mod_disco: {}
  mod_fail2ban: {}
  mod_http_api: {}
  mod_http_upload:
    put_url: https://@HOST@:5443/upload
    custom_headers:
      "Access-Control-Allow-Origin": "https://@HOST@"
      "Access-Control-Allow-Methods": "GET,HEAD,PUT,OPTIONS"
      "Access-Control-Allow-Headers": "Content-Type"
  mod_last: {}
  mod_mam:
    ## Mnesia is limited to 2GB, better to use an SQL backend
    ## For small servers SQLite is a good fit and is very easy
    ## to configure. Uncomment this when you have SQL configured:
    ## db_type: sql
    assume_mam_usage: true
    default: always
  mod_mqtt: {}
  mod_muc:
    access:
      - allow
    access_admin:
      - allow: admin
    access_create: muc_create
    access_persistent: muc_create
    access_mam:
      - allow
    default_room_options:
      mam: true
  mod_muc_admin: {}
  mod_offline:
    access_max_user_messages: max_user_offline_messages
  mod_ping: {}
  mod_privacy: {}
  mod_private: {}
  mod_proxy65:
    access: local
    max_connections: 5
  mod_pubsub:
    access_createnode: pubsub_createnode
    plugins:
      - flat
      - pep
    force_node_config:
      ## Avoid buggy clients to make their bookmarks public
      storage:bookmarks:
        access_model: whitelist
  mod_push: {}
  mod_push_keepalive: {}
  mod_register:
    ## Only accept registration requests from the "trusted"
    ## network (see access_rules section above).
    ## Think twice before enabling registration from any
    ## address. See the Jabber SPAM Manifesto for details:
    ## https://github.com/ge0rg/jabber-spam-fighting-manifesto
    ip_access: all
  mod_roster:
    versioning: true
  mod_s2s_dialback: {}
  mod_shared_roster: {}
  mod_stream_mgmt:
    resend_on_timeout: if_offline
  mod_stun_disco: {}
  mod_vcard: {}
  mod_vcard_xupdate: {}
  mod_version:
    show_os: false

### Local Variables:
### mode: yaml
### End:
### vim: set filetype=yaml tabstop=8`;
