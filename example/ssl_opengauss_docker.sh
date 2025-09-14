#!/bin/bash

# Script to set up OpenGauss with certificates, configuration, and Docker container

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Error handling function
error_exit() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1" >&2
    # if [ -n "$(docker ps -a -q -f name=^/$CONTAINER_NAME$)" ]; then
    #     log "$LINENO:Container logs for $CONTAINER_NAME:"
    #     docker logs "$CONTAINER_NAME" >&2
    #     log "$LINENO:Contents of $DATA_DIR inside container:"
    #     docker exec "$CONTAINER_NAME" ls -l $DATA_DIR 2>/dev/null || echo "Failed to list $DATA_DIR"
    # fi
    exit 1
}

wait_for_db() {
    local cname="$1"
    local max=60
    local i=0
    log "$LINENO: Waiting for $cname to be ready"

    # Check if the container is running
    if ! docker ps -q -f name="$cname" > /dev/null; then
        log "ERROR: Container $cname not running!"
        exit 1
    fi

    until docker exec "$cname" su - omm -c "gsql -c '\q'" >/dev/null 2>&1; do
        ((i++))
        if (( i>=max )); then
            log "ERROR: $cname not ready"
            exit 1
        fi
        sleep 5
        log "$LINENO: Waiting $cname ..."
    done

    log "$LINENO: $cname is ready"
}

# Check if running as root
if [ "$(id -u)" != "0" ]; then
    error_exit "This script must be run as root or with sudo."
fi

# Check if required commands are available
command -v openssl >/dev/null 2>&1 || error_exit "openssl is required but not installed."
command -v docker >/dev/null 2>&1 || error_exit "docker is required but not installed."
command -v netstat >/dev/null 2>&1 || error_exit "netstat is required but not installed."

# Check Docker service status
if ! systemctl is-active --quiet docker; then
    error_exit "Docker service is not running. Please start it with 'systemctl start docker'."
fi

# Define base directory and container name
BASE_DIR="/opengauss8889"
CERT_DIR="$BASE_DIR/certs"
CONF_DIR="$BASE_DIR/conf"
DATA_DIR="/var/lib/opengauss/data"
CONTAINER_NAME="opengauss-cp"
IMAGE_NAME="opengauss/opengauss-server:latest"
GPWD="Password@123"
PORT="8889"

# Remove existing container if it exists
log "$LINENO:Checking for existing container $CONTAINER_NAME"
if docker ps -a --format '{{.Names}}' | grep -w "$CONTAINER_NAME" >/dev/null 2>&1; then
    log "$LINENO:Removing existing container $CONTAINER_NAME"
    docker rm -f "$CONTAINER_NAME" || error_exit "Failed to remove container $CONTAINER_NAME"
else
    log "$LINENO:No existing container $CONTAINER_NAME found"
fi

# Remove existing directory if it exists
if [ -d "$BASE_DIR" ]; then
    log "$LINENO:Removing existing directory $BASE_DIR"
    rm -rf "$BASE_DIR" || error_exit "Failed to remove directory $BASE_DIR"
fi



# Create certificate and configuration directories
log "$LINENO:Creating directories: $CERT_DIR and $CONF_DIR"
mkdir -p "$CERT_DIR" "$CONF_DIR" || error_exit "Failed to create directories $CERT_DIR or $CONF_DIR"
cd "$CERT_DIR" || error_exit "Failed to change to directory $CERT_DIR"

# Generate CA certificate
log "$LINENO:Generating CA certificate"
openssl genrsa -out ca.key 4096 || error_exit "Failed to generate CA key"
openssl req -x509 -new -nodes -key ca.key -sha256 -days 3650 \
    -subj "/C=CN/ST=OpenGauss/L=OpenGauss/O=MyOrg/OU=DB/CN=OpenGaussCA" \
    -out ca.crt || error_exit "Failed to generate CA certificate"

# Generate server certificate
log "$LINENO:Generating server certificate"
openssl genrsa -out server.key 2048 || error_exit "Failed to generate server key"
openssl req -new -key server.key \
    -subj "/C=CN/ST=OpenGauss/L=OpenGauss/O=MyOrg/OU=DB/CN=opengauss.local" \
    -out server.csr || error_exit "Failed to generate server CSR"

# Create SAN configuration
log "$LINENO:Creating SAN configuration"
cat > san.cnf <<EOF
[ req ]
default_bits = 2048
distinguished_name = req_distinguished_name
req_extensions = req_ext
[ req_distinguished_name ]
[ req_ext ]
subjectAltName = @alt_names
[ alt_names ]
DNS.1 = opengauss.local
IP.1 = 127.0.0.1
EOF
[ -f san.cnf ] || error_exit "Failed to create SAN configuration file"

# Sign server certificate with CA
log "$LINENO:Signing server certificate"
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial \
    -out server.crt -days 730 -sha256 -extfile san.cnf -extensions req_ext \
    || error_exit "Failed to sign server certificate"

# Generate client certificate (for mutual TLS)
log "$LINENO:Generating client certificate"
openssl genrsa -out client.key 2048 || error_exit "Failed to generate client key"
openssl req -new -key client.key -subj "/CN=root" -out client.csr \
    || error_exit "Failed to generate client CSR"
openssl x509 -req -in client.csr -CA ca.crt -CAkey ca.key -CAcreateserial \
    -out client.crt -days 730 -sha256 || error_exit "Failed to sign client certificate"

# Create PostgreSQL configuration
log "$LINENO:Creating postgresql.conf"
cat > "$CONF_DIR/postgresql.conf" <<EOF
max_connections = 200			# (change requires restart)
session_timeout = 10min			# allowed duration of any unused session, 0s-86400s(1 day), 0 is disabled
bulk_write_ring_size = 2GB		# for bulkload, max shared_buffers
max_prepared_transactions = 200		# zero disables the feature
cstore_buffers = 512MB         #min 16MB
enable_incremental_checkpoint = on	# enable incremental checkpoint
incremental_checkpoint_timeout = 60s	# range 1s-1h
enable_double_write = on		# enable double write
wal_keep_segments = 16		# in logfile segments, 16MB each normal, 1GB each in share storage mode; 0 disables
enable_slot_log = off
synchronous_standby_names = '*'	# standby servers that provide sync rep
walsender_max_send_size = 8MB  # Size of walsender max send size
hot_standby = on			# "on" allows queries during recovery
enable_kill_query = off			# optional: [on, off], default: off
logging_collector = on   		# Enable capturing of stderr and csvlog
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'	# log file name pattern,
log_file_mode = 0600			# creation mode for log files,
log_rotation_size = 20MB		# Automatic rotation of logfiles will
log_min_duration_statement = 1800000	# -1 is disabled, 0 logs all statements
log_connections = off			# log connection requirement from client
log_disconnections = off		# log disconnection from client
log_duration = off			# log the execution time of each query
log_hostname = off			# log hostname
log_line_prefix = '%m %u %d %h %p %S '	# special values:
log_timezone = 'UCT'
enable_alarm = on
connection_alarm_rate = 0.9
alarm_report_interval = 10
alarm_component = '/opt/snas/bin/snas_cm_cmd'
use_workload_manager = on		# Enables workload manager in the system.
datestyle = 'iso, mdy'
timezone = 'UCT'
lc_messages = 'en_US.utf8'			# locale for system error message
lc_monetary = 'en_US.utf8'			# locale for monetary formatting
lc_numeric = 'en_US.utf8'			# locale for number formatting
lc_time = 'en_US.utf8'				# locale for time formatting
default_text_search_config = 'pg_catalog.english'
lockwait_timeout = 1200s		# Max of lockwait_timeout and deadlock_timeout +1s
pgxc_node_name = 'gaussdb'			# Coordinator or Datanode name
audit_enabled = on
job_queue_processes = 10        # Number of concurrent jobs, optional: [0..1000], default: 10.
dolphin.nulls_minimal_policy = on # the inverse of the default configuration value ! do not change !
password_encryption_type = 0
wal_level = logical
application_name = ''
listen_addresses = '*'
max_replication_slots = 10
max_wal_senders = 10
shared_buffers = 512MB
ssl = on
ssl_cert_file = '/var/lib/opengauss/certs/server.crt'
ssl_key_file = '/var/lib/opengauss/certs/server.key'
ssl_ca_file = '/var/lib/opengauss/certs/ca.crt'
EOF
[ -f "$CONF_DIR/postgresql.conf" ] || error_exit "Failed to create postgresql.conf"

# Create pg_hba.conf
log "$LINENO:Creating pg_hba.conf"
cat > "$CONF_DIR/pg_hba.conf" <<EOF
local   all             all                                     trust
host    all             all             127.0.0.1/32            trust
host    all             all             ::1/128                 trust
host all all 0.0.0.0/0 md5
hostssl all all 0.0.0.0/0 cert
host replication gaussdb 0.0.0.0/0 md5
EOF
[ -f "$CONF_DIR/pg_hba.conf" ] || error_exit "Failed to create pg_hba.conf"

# Check if Docker image exists locally, pull if not
log "$LINENO:Checking for Docker image $IMAGE_NAME"
if ! docker image inspect "$IMAGE_NAME" >/dev/null 2>&1; then
    log "$LINENO:Pulling Docker image $IMAGE_NAME"
    for i in {1..3}; do
        if docker pull "$IMAGE_NAME"; then
            break
        else
            log "$LINENO:Retrying pull ($i/3)..."
            sleep 5
        fi
    done || error_exit "Failed to pull Docker image $IMAGE_NAME after retries"
else
    log "$LINENO:Docker image $IMAGE_NAME already exists locally"
fi

# Run OpenGauss container without data directory mount
log "$LINENO:Running OpenGauss container"
docker run --name "$CONTAINER_NAME" --privileged=true -d \
    -e GS_USERNAME=root \
    -e GS_USER_PASSWORD=$GPWD \
    -e GS_PASSWORD=$GPWD \
    -p $PORT:5432 \
    -v "$BASE_DIR:/var/lib/opengauss" \
    -v "$CERT_DIR:/var/lib/opengauss/certs" \
    "$IMAGE_NAME" > /dev/null

# Wait for container to be running with timeout
log "$LINENO:OpenGauss Database Docker Container created."
wait_for_db "$CONTAINER_NAME"
log "$LINENO:OpenGauss Database is ready."

docker cp $CONF_DIR/postgresql.conf "$CONTAINER_NAME":/var/lib/opengauss/data/postgresql.conf
docker cp $CONF_DIR/pg_hba.conf "$CONTAINER_NAME":/var/lib/opengauss/data/pg_hba.conf


# Set permissions inside container and verify readability
log "$LINENO:Setting permissions for certificate files"
docker exec "$CONTAINER_NAME" bash -c "
    OWNER=\$(stat -c '%U' \"$DATA_DIR\" 2>/dev/null || echo omm)
    chown \"\$OWNER\":\"\$OWNER\" /var/lib/opengauss/certs/*
    chmod 600 /var/lib/opengauss/certs/*
    su - \"\$OWNER\" -c 'test -r /var/lib/opengauss/certs/server.crt' || exit 1
" || error_exit "Failed to set permissions or OpenGauss user cannot read certificate files"

# Verify certificate files
log "$LINENO:Verifying certificate files"
docker exec "$CONTAINER_NAME" ls -l /var/lib/opengauss/certs || error_exit "Failed to list certificate files"

# Restart container to apply changes
log "$LINENO:Restarting container"
docker restart "$CONTAINER_NAME" || error_exit "Failed to restart container"

# Wait for container to be running after restart with timeout
log "$LINENO:Waiting for container to be running after restart"
wait_for_db "$CONTAINER_NAME"
log "$LINENO:OpenGauss Database restart is ready."


# Create database if not exists
log "$LINENO:Creating test database"
docker exec "$CONTAINER_NAME" su - omm -c "gsql -c 'CREATE DATABASE test;'" 

log "$LINENO:Setup completed successfully"